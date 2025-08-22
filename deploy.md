

╔══════════════════════════════ Nixpacks v1.38.0 ══════════════════════════════╗

║ setup      │ python3, gcc                                                    ║

║──────────────────────────────────────────────────────────────────────────────║

║ install    │ python -m venv --copies /opt/venv && . /opt/venv/bin/activate   ║

║            │ && pip install -r requirements.txt                              ║

║──────────────────────────────────────────────────────────────────────────────║

║ start      │ python odds_mcp_v2.py                                           ║

╚══════════════════════════════════════════════════════════════════════════════╝

[internal] load build definition from Dockerfile

[internal] load build definition from Dockerfile  ✔ 0 ms

[internal] load build definition from Dockerfile

[internal] load build definition from Dockerfile  ✔ 10 ms

[internal] load metadata for ghcr.io/railwayapp/nixpacks:ubuntu-1745885067

[internal] load metadata for ghcr.io/railwayapp/nixpacks:ubuntu-1745885067  ✔ 72 ms

[internal] load .dockerignore

[internal] load .dockerignore  ✔ 0 ms

[internal] load .dockerignore

[internal] load .dockerignore  ✔ 11 ms

[stage-0 8/8] COPY . /app

[stage-0 7/8] RUN printf '\nPATH=/opt/venv/bin:$PATH' >> /root/.profile

[stage-0 6/8] RUN --mount=type=cache,id=s/c2407e22-58e0-4317-ae96-c3dd6f9d24a7-/root/cache/pip,target=/root/.cache/pip python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt

[stage-0 5/8] COPY . /app/.

[stage-0 4/8] RUN nix-env -if .nixpacks/nixpkgs-bc8f8d1be58e8c8383e683a06e1e1e57893fff87.nix && nix-collect-garbage -d

[stage-0 3/8] COPY .nixpacks/nixpkgs-bc8f8d1be58e8c8383e683a06e1e1e57893fff87.nix .nixpacks/nixpkgs-bc8f8d1be58e8c8383e683a06e1e1e57893fff87.nix

[internal] load build context

[stage-0 2/8] WORKDIR /app/

[stage-0 1/8] FROM ghcr.io/railwayapp/nixpacks:ubuntu-1745885067@sha256:d45c89d80e13d7ad0fd555b5130f22a866d9dd10e861f589932303ef2314c7de

[stage-0 1/8] FROM ghcr.io/railwayapp/nixpacks:ubuntu-1745885067@sha256:d45c89d80e13d7ad0fd555b5130f22a866d9dd10e861f589932303ef2314c7de

[internal] load build context

[internal] load build context  ✔ 0 ms

[internal] load build context

[internal] load build context  ✔ 12 ms

[stage-0 2/8] WORKDIR /app/  ✔ 0 ms – CACHED

[stage-0 3/8] COPY .nixpacks/nixpkgs-bc8f8d1be58e8c8383e683a06e1e1e57893fff87.nix .nixpacks/nixpkgs-bc8f8d1be58e8c8383e683a06e1e1e57893fff87.nix  ✔ 0 ms – CACHED

[stage-0 4/8] RUN nix-env -if .nixpacks/nixpkgs-bc8f8d1be58e8c8383e683a06e1e1e57893fff87.nix && nix-collect-garbage -d  ✔ 0 ms – CACHED

[stage-0 5/8] COPY . /app/.  ✔ 0 ms – CACHED

[stage-0 6/8] RUN --mount=type=cache,id=s/c2407e22-58e0-4317-ae96-c3dd6f9d24a7-/root/cache/pip,target=/root/.cache/pip python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt  ✔ 0 ms – CACHED

[stage-0 7/8] RUN printf '\nPATH=/opt/venv/bin:$PATH' >> /root/.profile  ✔ 0 ms – CACHED

[stage-0 8/8] COPY . /app  ✔ 1 ms – CACHED

[auth] sharing credentials for production-us-east4-eqdc4a.railway-registry.com

[auth] sharing credentials for production-us-east4-eqdc4a.railway-registry.com  ✔ 0 ms

importing to docker

importing to docker  ✔ 10 sec

=== Successfully Built! ===

Run:

docker run -it production-us-east4-eqdc4a.railway-registry.com/c2407e22-58e0-4317-ae96-c3dd6f9d24a7:804e3613-d061-478f-83e5-283cdd1ab0d0

Build time: 13.29 seconds