# 错位创意生成器

短剧素材创意生成工具 - 为广告优化师打造

## 快速部署到 Streamlit

1. **将代码推送到 GitHub**
   ```bash
   git add .
   git commit -m "迁移到Streamlit"
   git push
   ```

2. **部署到 Streamlit**
   - 访问 https://share.streamlit.io
   - 用 GitHub 登录
   - 选择这个仓库
   - 设置：
     - App file: `app.py`
     - Requirements file: `requirements.txt`
   - 点击 Deploy

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 功能

- 🎣 **钩子生成** - 基于错位类型自动生成吸引点击的创意
- 📦 **素材衔接** - 自然过渡到目标短剧/产品
- 🔧 **调试模式** - 可查看 Prompt 和 API 响应
