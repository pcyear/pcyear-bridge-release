# 多源音乐桥 · SongLoft 插件发布源（plugin/songloft）

本目录仅存放「多源音乐桥」插件的发布产物（源码见总项目 `pcyear-bridge/plugin/songloft/`），供 SongLoft 商店/订阅源拉取。

- `plugin.json` — 插件元信息（含 `updateUrl` → manifest.json）
- `manifest.json` — 版本 + 安装包下载地址
- `registry.json` — 自有订阅源入口
- `dist/multisource-music.jsplugin.zip` — 安装包

## 使用

在 SongLoft「插件商店 → 管理订阅源」添加：

```
https://gitee.com/pcyear/pcyear-bridge-release/raw/master/plugin/songloft/registry.json
```

> ⚠️ 仓库已由 `pcyear-songloft-plugin` 重命名为 `pcyear-bridge-release`，且发布物已从根目录移入 `plugin/songloft/`。
> 若尚未在 Gitee 完成对应仓库重命名，请先将 Gitee 仓库改名为 `pcyear-bridge-release`，并同步更新本目录 `plugin.json` 中的 `updateUrl` / `homepage`。

## 发布新版本

1. 在源码仓 `pcyear-bridge/plugin/songloft/` 重新构建插件（`npm run build`），得到 `dist/multisource-music.jsplugin.zip`
2. 把新 zip 覆盖到本目录 `dist/multisource-music.jsplugin.zip`
3. 更新本目录 `plugin.json` 的 `version`、`manifest.json` 的 `version`
4. commit + push 本仓库（`pcyear-bridge-release`）

## 远程部署

`deploy_remote.py` 可一键上传并热重载到远程 SongLoft（默认 `<宿主地址>:<端口>`）：

```bash
# 默认从同级源码仓 pcyear-bridge/plugin/songloft/dist 取 zip
python plugin/songloft/deploy_remote.py
# 或显式指定源码仓 / 产物目录
PLUGIN_SRC=/path/to/pcyear-bridge/plugin/songloft python plugin/songloft/deploy_remote.py
# 部署到本机 SongLoft
DEPLOY_HOST=http://<宿主地址>:<端口> DEPLOY_USER=<账号> DEPLOY_PASS=<密码> python plugin/songloft/deploy_remote.py
```
