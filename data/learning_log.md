# Learning Log

Sessions where Camille learnt a great deal from Claude.
Format: `YYYY-MM-DD | <project> | <description>`

---

2026-03-12 | audio-intelligence-pipeline | FastAPI + Docker + Hetzner deployment — REST API anatomy, HTTP methods, Pydantic, Uvicorn, Docker layer caching, port mapping, PAT auth
2026-03-13 | audio-intelligence-pipeline | Docker deployment from scratch: containers, ports, firewalls, VPS — full conceptual walkthrough including building/apartment analogy, firewall rules, MLflow security middleware debugging
2026-03-13 | audio-intelligence-pipeline | MLflow 3.x GenAI evaluation primitives: Judges tab (@mlflow.genai.scorer), Datasets, Evaluation runs vs old mlflow.evaluate()+make_metric — what each UI section means and when to use which API
2026-03-27 | general | Docker vs Docker Compose vs Kubernetes — differences, use cases, decision matrix, and the single-host → multi-host progression mental model
2026-03-13 | finances-ezerpin | GitHub auth patterns for servers: deploy key vs PAT, fine-grained vs classic tokens, Docker per-project isolation rationale
2026-03-16 | finances-ezerpin | dbt Core vs Fusion, dbt_project.yml anatomy (name vs profile, config-version, clean-targets, model materializations), profiles.yml (dev vs prod targets), --project-dir vs --profiles-dir flags, local dev sandbox vs Hetzner prod DuckDB
2026-03-13 | .claude | Bootcamp project evaluation: scoring 15+ projects against C1-C5 data engineering criteria, French open data sources (assemblee-nationale.fr API, DVF dataset), scraping vs official API feasibility trade-offs
2026-03-24 | ai-networking-system | Hetzner deploy walkthrough: Docker containers vs Dockerfile vs docker-compose.yml, port binding (0.0.0.0 vs 127.0.0.1), health endpoints, GitHub SSH key setup on server, bearer token generation, nginx reverse proxy concepts
2026-03-25 | general | GitHub auth systems: SSH keys (badge per machine) vs fine-grained PAT (scoped authorization letter per tool) vs classic PAT (broad legacy letter) — when to use each, how to audit existing tokens, badge/letter analogy
2026-03-25 | ai-networking-system | DNS explained: phonebook analogy, A records, dig command, why DNS must resolve before certbot can issue SSL — discovered crm-api.helmcome.com has no A record yet
2026-03-25 | ai-networking-system | Two-layer firewall model: Hetzner Cloud FW (external, whitelist, blocks before reaching server) vs ufw (internal OS, deny-all when active) — why ufw allow 22 must precede ufw enable, why Hetzner is whitelist not default-open
2026-03-26 | ai-networking-system | CRM API anatomy: what FastAPI + DuckDB is, why it exists (n8n can't query DuckDB directly, needs HTTP bridge), all endpoints and their purpose, Bearer token auth — plus project dependency chain clarification: Audio Pipeline → UC5/Meeting Note Taker → Media Content Manager
2026-03-26 | hetzner-infra | Terraform from scratch: what IaC is (blueprint analogy), hcloud CLI setup, provider/variables/modules/tfvars structure, terraform init (contractor delivering tools), plan vs apply, prevent_destroy, why modules need required_providers declared, HCLOUD_TOKEN + TF_VAR_ env var pattern
2026-03-30 | pea-pme-pulse | Data source validation (Boursorama scraping, AMF API v2, RSS feeds), ISIN as pivot key across 5 sources, medallion architecture design (Bronze/Silver/Gold), jointure/mapping strategy per source, pyproject.toml anatomy + pip install -e ".[dev]" explained
