### pyright tool
---

`bin/` - pyright打包后的可执行工具，使用`pkg`打包    

`config/pyrightconfig.json` - 默认配置文件，根据所选规则进行动态调整   

`src/main.py` - 执行入口   

---

#### 使用：

请注意，使用 `pyright` 工具的规则时，需要在环境变量中设置两个环境变量
- pyright_stubs_path : 项目的存根文件夹，否则无法解析外部包的类型，请填写文件夹相对路径, 如 projectName/stubs
- pyright_python_version: 项目所使用的python版本，请填写版本号 ，如 3.8