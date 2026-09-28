# 池间 · 互动鱼塘

一个可互动的手绘鱼塘场景原型，支持鱼群游动、鼠标躲避、点击投食、自定义小鱼、昼夜、天气和季节氛围。

## 本地运行

```powershell
npm install
npm run dev -- --port 5178
```

打开 `http://127.0.0.1:5178/`。

## 常用命令

```powershell
npm test
npm run build
npm run test:e2e
```

## 当前功能

- 四款锦鲤、鲤鱼、金鱼、草鱼、泥鳅，共八款手绘鱼素材
- 鱼群躲避、追食、重新聚拢；不同水深交错游动，追食时逐渐上浮
- 乌龟浮水、蝴蝶与蜻蜓振翅、夜间萤火虫
- 白鹭和燕子交替掠过，独立鸟影；落叶从空中落下后随水漂动
- 晴天、阴天、雨天、雾天、雪天、暴雨
- 春夏秋冬氛围
- 当地天气与手动天气切换
- 默认完整动态效果，无画质或强度档位；保留安静模式和系统减少动态偏好
- 画鱼、保存、编辑和放入鱼塘

Wallpaper Engine 宿主适配和多显示器能力尚未接入。

## 素材与验证

新增生态素材使用 Quya 的 `gpt-image-2.5-sunburst` 模型生成，提示词在
`scripts/ecology-prompts.json`，来源与原图校验值在 `public/assets/ecology/provenance.json`。
重新生成需在进程环境中设置 `IMAGE_MODEL_API_KEY`，然后执行
`node scripts/generate-ecology.mjs`。密钥不得写入前端、提示词或版本库。

浏览器测试使用本机 Microsoft Edge，覆盖桌面、全高清、QHD 和竖屏。
除交互流程外，还验证真实素材像素、翅膀网格运动、鱼的深度排序、
雨滴可见像素和昼夜昆虫切换；截图保存在被 Git 忽略的 `artifacts/`。
