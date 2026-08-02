# 1vivy personal crDroid 16.0 ROM manifest

Personal ROM composition for OnePlus SM8850 — `infiniti`, `macan`, `macanc`,
`fairlady` — consuming the published
[`infiniti-camera-port`](https://github.com/infiniti-camera-port) camera graph.

## Quick start

```sh
mkdir rom && cd rom
repo init -u https://github.com/crdroidandroid/android.git -b 16.0
mkdir -p .repo/local_manifests
curl -o .repo/local_manifests/1vivy-rom.xml \
  https://raw.githubusercontent.com/1vivy/1vivy-rom_local_manifest/main/local_manifests/1vivy-rom.xml
repo sync -c -j8
```

Then apply the camera-port profile — see below, it is **mandatory** here.

## This is the outside-developer composition, not the promoted graph

There are two valid ways to consume the camera-port work, and mixing them
double-applies every patch:

| | `infiniti-camera-port/local_manifest` | **this manifest** |
|---|---|---|
| eight source repos pinned at | promoted heads | profile **base** commits |
| series already in the tree | yes | no |
| run `patch/` profile | **never** | **always** |

This manifest exists to prove the published profile actually works from a clean
room, the way an outside porter would use it. After `repo sync`, follow the
*Downstream porter quick start* in the
[`patches`](https://github.com/infiniti-camera-port/patches) README: run
`apply-patches.py` in check mode against profile `infiniti-crdroid-16.0`, then
`repo start infiniti-crdroid-16.0` across the eight targets, then run it again
in apply mode. Each target then reaches the promoted contract head.

## Composition

- **Base** — crDroid `16.0`, pinned at `aac17d7a4a7b1e09f5ca5cb0f517ac0d73cfac91`.
- **Eight profile targets** — pinned at their `series.json` `base_sha`; the
  profile carries them to the promoted heads.
- **Five device trees** — `1vivy/*` forks on `16.0`, cut at an immutable
  pre-lane pin table rather than at fork tips. For `device/oneplus/infiniti`
  and `device/oneplus/sm8850-common` the lane tip *is* the profile base
  (`ba57c74670f9`, `0522cdc6164b`), so the profile applies directly.
- **Sync-only inputs** — the six declared profile prerequisites plus the
  camera/blob repos closing source for the other three devices. Never patch
  targets.
- **Non-matrix closure** — kernel, audio-ar, qcom-caf common/thermal/usb,
  unchanged from the promoted graph.

36 projects, 34 removals.

## Build

```sh
source build/envsetup.sh
lunch lineage_infiniti-bp4a-userdebug
mka bacon
```

Only `infiniti` is built and runtime-validated upstream. `macan`, `macanc` and
`fairlady` are present for source closure and static lunch resolution — no
runtime result is implied for them.

## LFS

Several proprietary repos are Git LFS backed. If a blob arrives as a ~130-byte
file beginning `version https://git-lfs.github.com/spec/v1`, it was not
hydrated; run `git -C <repo> lfs pull`. To find every such file at once:

```sh
find . -type f -size -400c -not -path "*/.git/*" -not -path "./out/*" -print0 \
  | xargs -0 -P 16 -n 300 grep -l "^version https://git-lfs"
```
