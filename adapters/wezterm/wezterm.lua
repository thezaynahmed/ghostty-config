-- WezTerm Config - Dyslexia + ADHD + Late-Night Edition
local wezterm = require 'wezterm'
local config = wezterm.config_builder and wezterm.config_builder() or {}

config.font = wezterm.font_with_fallback({
  { family = 'Monaspace Neon', harfbuzz_features = { 'calt=1', 'ss01=1', 'ss02=1', 'ss03=1', 'zero=1', 'cv10=1' } },
})
config.font_rules = {
  {
    italic = true,
    font = wezterm.font('Monaspace Radon', { italic = false }),
  },
}
config.font_size = 14.5
config.line_height = 1.20
config.cell_width = 1.04
config.freetype_load_target = 'Light'
config.front_end = 'WebGpu'

config.default_cursor_style = 'SteadyBlock'
config.cursor_blink_rate = 0
config.window_background_opacity = 1.0
config.macos_window_background_blur = 0
config.window_padding = { left = 14, right = 14, top = 12, bottom = 12 }

config.inactive_pane_hsb = {
  saturation = 0.85,
  brightness = 0.65,
}

config.colors = {
  foreground = '#d4be98',
  background = '#282828',
  cursor_bg = '#d4be98',
  cursor_fg = '#282828',
  selection_bg = '#45403d',
  selection_fg = '#d4be98',
  ansi = { '#282828', '#ea6962', '#a9b665', '#d8a657', '#7daea3', '#d3869b', '#89b482', '#d4be98' },
  brights = { '#7c6f64', '#ea6962', '#a9b665', '#d8a657', '#7daea3', '#d3869b', '#89b482', '#ddc7a1' },
}

return config
