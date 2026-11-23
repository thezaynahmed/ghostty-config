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
  foreground = '#d8d6cf',
  background = '#15171a',
  cursor_bg = '#f0c946',
  cursor_fg = '#111316',
  selection_bg = '#323a46',
  selection_fg = '#eceae4',
  ansi = { '#15171a', '#e86a74', '#63c794', '#f0c946', '#74aeeb', '#b695e8', '#68c5ce', '#d8d6cf' },
  brights = { '#878d96', '#f28b94', '#7ed8a9', '#f7d96d', '#93c2f2', '#c8aef0', '#84d6de', '#eceae4' },
}

return config
