# github-workflows

Reusable GitHub Actions workflows.

## Workflows

### `qodana.yml`

Wraps `JetBrains/qodana-action` with `actions/checkout`, optional GitHub-hosted runner disk cleanup (`runner.environment == 'github-hosted'`), and `actions/setup-java`.

| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `runner` | `string` | `ubuntu-latest` | Target runner label or expression |
| `java-distribution` | `string` | `corretto` | JDK distribution for `actions/setup-java` |
| `java-version` | `string` | *(required)* | JDK version for `actions/setup-java` |
| `args` | `string` | `''` | Extra arguments passed to `JetBrains/qodana-action` |
| `use-caches` | `boolean` | `true` | Enable Qodana caches |
| `pr-mode` | `boolean` | `true` | Enable PR mode when triggered on `pull_request` |
| `timeout-minutes` | `number` | `60` | Job timeout in minutes |

- **Secret:** `QODANA_TOKEN` (optional)
- **Caller permissions:** grant at least `contents: read`, `checks: write`, and `pull-requests: write` on the calling job.

```yaml
jobs:
  qodana:
    permissions:
      contents: read
      checks: write
      pull-requests: write
    uses: wubli/github-workflows/.github/workflows/qodana.yml@master
    with:
      runner: ubuntu-latest
      java-distribution: corretto
      java-version: '25'
      args: --project-dir backend
    secrets:
      QODANA_TOKEN: ${{ secrets.QODANA_TOKEN }}
```

### `docker-ghcr.yml`

Wraps `docker/setup-buildx-action`, optional branch-HEAD stale-run guard, `docker/login-action` to `ghcr.io` (using `github.token`), `docker/metadata-action`, and `docker/build-push-action`.

| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `runner` | `string` | `ubuntu-latest` | Target runner label or expression |
| `context` | `string` | `.` | Docker build context |
| `file` | `string` | `''` | Optional Dockerfile path |
| `image` | `string` | `''` | Target image name (defaults to `ghcr.io/<owner>/<repo>`) |
| `push` | `boolean` | `false` | Push built image to GHCR |
| `guard-branch` | `string` | `''` | When `push` is true, skip push if `heads/<guard-branch>` moved past `github.sha` |
| `metadata-tags` | `string` | `latest` on default branch + full `sha` | Newline-delimited tags passed to `docker/metadata-action` |
| `max-parallelism` | `number` | `2` | BuildKit `[worker.oci]` `max-parallelism` |
| `timeout-minutes` | `number` | `45` | Job timeout in minutes |

- **Caller permissions:** pass `contents: read` when `push: false`, and `contents: read` + `packages: write` when `push: true`.

```yaml
jobs:
  publish-image:
    permissions:
      contents: read
      packages: write
    uses: wubli/github-workflows/.github/workflows/docker-ghcr.yml@master
    with:
      runner: ubuntu-latest
      context: .
      image: ghcr.io/${{ github.repository }}
      push: true
      guard-branch: main
```
