-- clean.lua
-- Pandoc Lua Filter to clean up redundant attributes and tags

-- 1. Remove all Spans, keeping their content
-- This strips <span lang="zh-CN">...</span> and other attribute-only containers
function Span(el)
  return el.content
end

-- 2. Remove all Divs, keeping their content
-- This strips <div class="...">...</div>
function Div(el)
  return el.content
end

-- 3. Remove Raw HTML (Inline)
-- This strips any leftover <tags> that Pandoc treated as raw HTML
function RawInline(el)
  if el.format:match 'html' then
    return {}
  else
    -- keep other raw formats if necessary, but usually safe to remove for Markdown output
    return {}
  end
end

-- 4. Remove Raw HTML (Block)
function RawBlock(el)
  if el.format:match 'html' then
    return {}
  else
    return {}
  end
end

-- 5. Clean up Image attributes (optional, GFM usually ignores them anyway)
-- But just in case
function Image(el)
  el.attr = pandoc.Attr() -- Clear attributes like width/height
  return el
end
