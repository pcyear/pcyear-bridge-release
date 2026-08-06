# pcyear-bridge-release

「多源音乐桥」(pcyear-bridge) 的**发布/发行仓库**，与源码仓 `pcyear-bridge` 分离，只放产物、不放源码。

```
pcyear-bridge-release/
├── app/                 # App 各平台发行产物：apk、安装包、打包配置（当前占位，待接入构建）
└── plugin/
    └── songloft/        # 曲库插件发布目录：打包产物 + 部署脚本
        ├── dist/multisource-music.jsplugin.zip
        ├── plugin.json / manifest.json / registry.json
        ├── static/      # 图标等静态资源
        └── deploy_remote.py   # 远程一键部署脚本
```

- 插件发布说明见 [`plugin/songloft/README.md`](./plugin/songloft/README.md)
- 源码与构建见源码仓 `pcyear-bridge/plugin/songloft/`

> 本仓库由旧 `pcyear-songloft-plugin`（发布仓）演化而来，目录规范化到 `plugin/songloft/` 下。
> 若从旧订阅源迁移，请把 SongLoft 订阅源地址更新为
> `https://gitee.com/pcyear/pcyear-bridge-release/raw/master/plugin/songloft/registry.json`。
