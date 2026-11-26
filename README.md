# github-workflows

Reusable GitHub Actions workflows.

## Workflows

### `qodana.yml`

Checks out the pull request head, or the triggering commit for other events,
with full Git history. The workflow frees disk space on GitHub-hosted runners,
sets up Java, and runs `JetBrains/qodana-action` with result uploads enabled.

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

Checks out the triggering revision and configures Buildx. When publishing,
the workflow logs in to `ghcr.io` with `github.token`. If `guard-branch` is
set, the workflow compares that branch's head with the triggering commit
before building and pushing the image. A different head skips the build and
push, and an API failure or missing SHA fails the job.

| Input | Type | Default | Description |
| --- | --- | --- | --- |
| `runner` | `string` | `ubuntu-latest` | Target runner label or expression |
| `context` | `string` | `.` | Docker build context |
| `file` | `string` | `''` | Optional Dockerfile path |
| `image` | `string` | `''` | Target image name (defaults to `ghcr.io/<owner>/<repo>`) |
| `push` | `boolean` | `false` | Push built image to GHCR |
| `guard-branch` | `string` | `''` | When `push` is true, build and push only if `heads/<guard-branch>` matches `github.sha` |
| `metadata-tags` | `string` | Full commit SHA with no prefix, plus `latest` on the default branch | Newline-delimited tags passed to `docker/metadata-action` when publishing or when `image` is set |
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
