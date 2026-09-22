-- Rebalance table column widths, and apply the guide's exact original
-- per-row category colors, emitting each table as raw LaTeX with plain
-- absolute widths (in inches) rather than pandoc's \real{}/calc-based
-- fractional widths (which breaks on some LaTeX installations).

local CONTENT_WIDTH_IN = 4.5
local TABCOLSEP_IN = 4 / 72.27  -- must match \setlength{\tabcolsep}{4pt} in the template

-- Exact row fill colors (hex, no #), extracted directly from the verified
-- print-book source. Keyed by (data-row-count, col-count) signature, since
-- these five tables are the only ones in the guide and each has a unique
-- shape. Row 0 in each list is the header row's fill; header text is
-- always rendered white/bold regardless.
local ROW_COLORS = {
  ["13x3"] = {"444441","EEEDFE","EEEDFE","E1F5EE","E1F5EE","FAECE7","FAECE7","DCEAF2","FAEEDA","FAEEDA","FAEEDA","F1EFE8","F1EFE8","F1EFE8"},
  ["8x3"]  = {"444441","EEEDFE","F1F0EA","EEEDFE","F1F0EA","EEEDFE","F1F0EA","EEEDFE","F1F0EA"},
  ["5x4"]  = {"444441","EEF7F1","FBEFE9","FBEFE9","FBEFE9","F7E2DB"},
  ["5x5"]  = {"444441","EEF7F1","EEF7F1","F1F0EA","EEEDFE","EEEDFE"},
  ["2x4"]  = {"444441","EEF7F1","EEF7F1"},
}

local function cell_to_latex(cell)
  local doc = pandoc.Pandoc(cell.contents)
  local latex = pandoc.write(doc, "latex")
  latex = latex:gsub("\r?\n", " ")
  latex = latex:gsub("%s+", " ")
  latex = latex:gsub("^%s+", "")
  latex = latex:gsub("%s+$", "")
  return latex
end

function Table(tbl)
  if #tbl.bodies ~= 1 then return tbl end
  if tbl.foot and tbl.foot.rows and #tbl.foot.rows > 0 then return tbl end

  local n = #tbl.colspecs
  if n == 0 then return tbl end

  local body = tbl.bodies[1]
  local n_data_rows = #body.body
  local sig = string.format("%dx%d", n_data_rows, n)
  local colors = ROW_COLORS[sig]

  local widths = {}
  local total = 0
  for i, cs in ipairs(tbl.colspecs) do
    local w = cs[2]
    if w == nil or w == 0 then w = 1.0 / n end
    widths[i] = w
    total = total + w
  end
  for i, w in ipairs(widths) do widths[i] = w / total end

  local minw = math.min(0.24, 0.85 / n)
  local deficit = 0
  for i, w in ipairs(widths) do
    if w < minw then
      deficit = deficit + (minw - w)
      widths[i] = minw
    end
  end
  if deficit > 0 then
    local abovesum = 0
    for i, w in ipairs(widths) do
      if w > minw then abovesum = abovesum + (w - minw) end
    end
    if abovesum > 0 then
      for i, w in ipairs(widths) do
        if w > minw then
          local excess = w - minw
          widths[i] = w - deficit * (excess / abovesum)
        end
      end
    end
  end

  -- Account for \tabcolsep padding between columns (n-1 internal gaps, each
  -- 2*tabcolsep wide) so the table's TOTAL rendered width -- not just the
  -- sum of column widths -- exactly matches \textwidth. Without this, the
  -- table silently renders wider than the surrounding paragraphs and its
  -- right edge creeps into what should be the page's right margin.
  local overhead_in = (n - 1) * 2 * TABCOLSEP_IN
  local usable_width_in = CONTENT_WIDTH_IN - overhead_in

  local colspec = {}
  for i = 1, n do
    colspec[i] = string.format(">{\\raggedright\\arraybackslash}p{%.3fin}", widths[i] * usable_width_in)
  end

  local lines = {}
  table.insert(lines, "\\begingroup\\small")
  table.insert(lines, "\\renewcommand{\\arraystretch}{1.15}")
  table.insert(lines, "\\begin{longtable}{@{}" .. table.concat(colspec, "") .. "@{}}")

  if #tbl.head.rows > 0 then
    if colors then
      table.insert(lines, string.format("\\rowcolor[HTML]{%s}", colors[1]))
    end
    for _, hrow in ipairs(tbl.head.rows) do
      local cells = {}
      for _, c in ipairs(hrow.cells) do
        local txt = cell_to_latex(c)
        if colors then txt = "\\textcolor{white}{\\textbf{" .. txt .. "}}"
        else txt = "\\textbf{" .. txt .. "}" end
        table.insert(cells, txt)
      end
      table.insert(lines, table.concat(cells, " & ") .. " \\\\")
    end
    table.insert(lines, "\\endhead")
  end

  for ri, row in ipairs(body.body) do
    if colors and colors[ri + 1] then
      table.insert(lines, string.format("\\rowcolor[HTML]{%s}", colors[ri + 1]))
    end
    local cells = {}
    for _, c in ipairs(row.cells) do
      table.insert(cells, cell_to_latex(c))
    end
    table.insert(lines, table.concat(cells, " & ") .. " \\\\[2pt]")
  end

  table.insert(lines, "\\end{longtable}")
  table.insert(lines, "\\endgroup")

  return pandoc.RawBlock("latex", table.concat(lines, "\n"))
end

local LATEX_ESCAPES = {
  ["\\"] = "\\textbackslash{}",
  ["{"] = "\\{",
  ["}"] = "\\}",
  ["_"] = "\\_",
  ["#"] = "\\#",
  ["%"] = "\\%",
  ["&"] = "\\&",
  ["^"] = "\\^{}",
  ["~"] = "\\~{}",
  ["$"] = "\\$",
}

-- Wrap a raw (unescaped) code line to at most maxw characters, breaking at
-- the last space found if one exists reasonably close to the limit, else
-- hard-breaking at the limit. Continuation lines get a small hanging
-- indent so wrapped code is visually distinguishable from a new line.
local MAX_CODE_WIDTH = 78

local function wrap_code_line(line, maxw)
  if #line <= maxw then return {line} end
  local pieces = {}
  local remaining = line
  local first = true
  while #remaining > maxw do
    local limit = first and maxw or (maxw - 2)
    local breakpos = nil
    for i = limit, math.floor(limit * 0.6), -1 do
      if remaining:sub(i, i) == " " then
        breakpos = i
        break
      end
    end
    if not breakpos then breakpos = limit end
    table.insert(pieces, first and remaining:sub(1, breakpos) or ("  " .. remaining:sub(1, breakpos)))
    remaining = remaining:sub(breakpos + 1):gsub("^%s+", "")
    first = false
  end
  table.insert(pieces, first and remaining or ("  " .. remaining))
  return pieces
end

function CodeBlock(block)
  local lines = {}
  table.insert(lines, "\\begin{shaded}\\small\\ttfamily\\noindent")
  for raw_line in (block.text .. "\n"):gmatch("([^\n]*)\n") do
    for _, line in ipairs(wrap_code_line(raw_line, MAX_CODE_WIDTH)) do
      local esc_line = line:gsub("[\\{}_#%%&%^~$]", LATEX_ESCAPES)
      -- Replace each space with a fixed-width phantom box matching one
      -- monospace character. This reliably preserves exact indentation
      -- regardless of catcode/active-character context (unlike "~", which
      -- can silently fail to render as a space inside certain environments
      -- such as framed's shaded box).
      esc_line = esc_line:gsub(" ", "\\hphantom{0}")
      table.insert(lines, esc_line .. "\\\\")
    end
  end
  table.insert(lines, "\\end{shaded}")
  return pandoc.RawBlock("latex", table.concat(lines, "\n"))
end

-- Force a page break before every chapter-level (H1) heading, and shrink
-- the font on figure-caption paragraphs (a lone italicized "Figure N. ..."
-- paragraph immediately following an image).
function Header(el)
  if el.level == 1 then
    return {pandoc.RawBlock("latex", "\\clearpage"), el}
  end
  return el
end

function Para(el)
  if #el.content == 1 and el.content[1].t == "Emph" then
    local emph_inlines = el.content[1].content
    if #emph_inlines > 0 and emph_inlines[1].t == "Str" and emph_inlines[1].text:match("^Figure") then
      local doc = pandoc.Pandoc({pandoc.Plain(el.content)})
      local latex = pandoc.write(doc, "latex")
      latex = latex:gsub("\r?\n", " ")
      return pandoc.RawBlock("latex", "{\\small " .. latex .. "\\par}")
    end
  end
  return el
end
