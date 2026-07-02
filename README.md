# AirMosaic AI Web

Website source project for **AirMosaic AI / 清空智枢**.

This repository is intended for GitHub upload. It should contain only website source code, UI components, API clients, mock data, and documentation. It must not contain raw environmental data, private tokens, or model outputs.

## Role

The web project is the visual and interaction layer. It should call `airmosaic-ai-core` services through REST/OpenAPI, MCP-aware gateway services, or a future SDK. It should not implement data acquisition or causal-model internals directly.

## Repository Boundary

This repository is safe to publish as a public GitHub repository. Keep raw datasets, credentials, private URLs, local outputs, and logs outside this repository.

## Current Site

The first static version is implemented with:

- Home decision surface for external Agent calls.
- Initial data catalog view.
- Service boundary cards for catalog, data access, acquisition, geospatial, model design, and causal design.
- Decision workflow and publish options.

## Preview

Run from this directory:

```powershell
python -m http.server 5176 --bind 127.0.0.1
```

Then open <http://127.0.0.1:5176/>.

Verified screenshots are saved in `docs/screenshots/`.

## GitHub Pages

This static site can be published from the repository root on the `main` branch.

1. Push this repository to GitHub.
2. Open repository `Settings > Pages`.
3. Set `Source` to `Deploy from a branch`.
4. Select branch `main` and folder `/ (root)`.
5. Save and wait for the Pages URL.

## Design Notes

See `docs/design-system-proposal.md` and `docs/publish-website.md`.

## License

Apache-2.0. See `LICENSE`.
