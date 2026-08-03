# pcyear 的 SongLoft 插件发布源

本仓库仅存放「多源音乐桥」插件的发布产物（源码不在此），供 SongLoft 商店/订阅源拉取。

- `plugin.json` — 插件元信息（含 `updateUrl` → manifest.json）
- `manifest.json` — 版本 + 安装包下载地址
- `registry.json` — 自有订阅源入口
- `dist/multisource-music.jsplugin.zip` — 安装包

## 使用

在 SongLoft「插件商店 → 管理订阅源」添加：

```
https://gitee.com/pcyear/pcyear-songloft-plugin/raw/master/registry.json
```

## 发布新版本

1. 重新构建插件，把新 zip 覆盖到 `dist/multisource-music.jsplugin.zip`
2. 更新 `plugin.json` 的 `version`、`manifest.json` 的 `version`
3. commit + push 本仓库
