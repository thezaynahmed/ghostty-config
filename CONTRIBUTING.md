# Contributing

Contributions, contrast measurements, and new terminal adapters are welcome.

## Adding or Tuning a Theme

1. Place any custom Ghostty theme file in [`themes/`](themes/) using Ghostty's `palette = N=#hex` format.
2. Check foreground-to-background luminance contrast against WCAG 2.0 (`>= 4.5:1` for primary body text and `>= 2.8:1` for muted `ANSI 8` comments).
3. Check the configuration with:
   ```bash
   ghostty +validate-config
   ```
4. Place any new terminal or IDE adapter inside [`adapters/`](adapters/) and document the file path in [`README.md`](README.md).

## License

By contributing, you agree that your contributions use the [MIT License](LICENSE).
