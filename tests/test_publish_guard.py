import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class PublishGuardTests(unittest.TestCase):
    def gate(self, head, error=False):
        workflow = Path(__file__).parents[1] / '.github' / 'workflows' / 'docker-ghcr.yml'
        block = workflow.read_text().split('      - name: Check current branch before publishing\n', 1)[1]
        self.assertIn('        uses: actions/github-script@', block)
        block = block.split('          script: |\n', 1)[1]
        script_lines = []
        for line in block.splitlines():
            if line.strip() and not line.startswith(' ' * 12):
                break
            script_lines.append(line[12:])
        script = '\n'.join(script_lines)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output = root / 'output'
            output.touch()
            env = os.environ | {
                'MASTER_HEAD': head,
                'API_ERROR': str(error).lower(),
                'GUARD_BRANCH': 'master',
                'GITHUB_OUTPUT': str(output),
            }
            stub = (
                "import fs from 'node:fs'; import assert from 'node:assert/strict';\n"
                "const context = { repo: { owner: 'example-org', repo: 'example-app' }, sha: 'target' };\n"
                "const github = { rest: { git: { getRef: async (request) => {\n"
                "  assert.deepEqual(request, { owner: 'example-org', repo: 'example-app', ref: 'heads/master' });\n"
                "  if (process.env.API_ERROR === 'true') throw new Error('API failure');\n"
                "  return { data: { object: { sha: process.env.MASTER_HEAD } } };\n"
                "} } } };\n"
                "const core = { setOutput: (key, value) => fs.appendFileSync(process.env.GITHUB_OUTPUT, `${key}=${value}\\n`) };\n"
            )
            result = subprocess.run(
                ['node', '--input-type=module', '--eval', stub + script],
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode, output.read_text().strip()

    def test_current_head_is_admitted_and_superseded_head_is_skipped(self):
        self.assertEqual(self.gate('target'), (0, 'current=true'))
        self.assertEqual(self.gate('newer'), (0, 'current=false'))

    def test_lookup_failure_does_not_admit_publication(self):
        self.assertEqual(self.gate('', error=True), (1, ''))

    def test_empty_lookup_does_not_admit_publication(self):
        self.assertEqual(self.gate(''), (1, ''))


if __name__ == '__main__':
    unittest.main()
