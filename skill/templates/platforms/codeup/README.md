# Codeup Change Request Default Flow

Codeup is the default hosted Git review platform for this skill. GitHub remains supported as an example platform, but adopting projects should start from this Codeup flow when they use Aliyun Yunxiao Codeup.

## Local Token

Codeup OpenAPI calls use a Yunxiao personal access token in the `x-yunxiao-token` request header. Each developer stores their own token locally as `YUNXIAO_TOKEN`.

Do not commit the token to `.claw/`, `docs/`, source code, task status files, or logs.

Recommended local setup:

```bash
python3 scripts/store-yunxiao-token.py
python3 scripts/configure-codeup-change-request.py
```

If `YUNXIAO_TOKEN` is missing, the Codeup create script stops before making an API request and prints the official token document:

https://help.aliyun.com/zh/yunxiao/developer-reference/obtain-personal-access-token

## Create A Change Request

`configure-codeup-change-request.py` writes platform configuration to `.claw-local/codeup.env`. You may also set values manually through CLI flags or shell environment variables:

```bash
export YUNXIAO_DOMAIN="https://openapi-rdc.aliyuncs.com"
export CODEUP_REPOSITORY_ID="2813489"
export CODEUP_SOURCE_PROJECT_ID="2813489"
export CODEUP_TARGET_PROJECT_ID="2813489"
export CODEUP_TARGET_BRANCH="master"
```

Create the change request:

```bash
python3 scripts/create-codeup-change-request.py \
  --source-branch feat/TASK-001-feature-title \
  --title "[TASK-001] Feature title" \
  --description-file .claw/tasks/TASK-001.md \
  --reviewer-user-ids "62c795xxxb468af8"
```

`CODEUP_REPOSITORY_ID` is the path parameter. It can be the numeric repository id or the URL-encoded full path. The request body still requires numeric `sourceProjectId` and `targetProjectId`; when `CODEUP_REPOSITORY_ID` is numeric, the script uses it as the default for both project ids.

For center-version Yunxiao endpoints, also provide:

```bash
export YUNXIAO_ORGANIZATION_ID="your-organization-id"
```

## Required Team Convention

- Branch names should include `TASK-xxx`.
- Change request titles should include `[TASK-xxx]`.
- Change request descriptions should include scope, verification, risk, and rollback notes.
- `.claw/tasks/TASK-xxx.md` should record `change_request_url` after creation.
- Protected branches should require Codeup review and Yunxiao Flow checks before merge.
- Flow checks should call `scripts/check-assignment.py` or an equivalent adapter before merge.

## GitHub Compatibility

The GitHub Actions example remains available at `templates/github-workflows/check-assignment.yml` for teams that use GitHub. It is not the default platform template.
