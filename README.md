### pyright tool 使用文档
---

**pyright工具介绍：**

Pyright是微软开源的项目，使用ts开发，开源协议为MIT，为vscode，sublime text等编辑器提供了插件形式的工具，方便开发者在编写代码的过程中使用pyriht 提供类型校验和代码提示


**工具目录说明：**

`bin/` - pyright打包后的可执行工具，使用`pkg`打包    

`config/pyrightconfig.json` - 默认配置文件，根据所选规则进行动态调整   

`src/main.py` - 执行入口   

**工具支持环境说明:**   
pyright支持在`windows`,`linux`,`macos`环境执行


**pyright规则:**
`pyright`默认使用 `basic` 模式，且暂不支持使用用户的项目中的配置
其中包含 22 个规则

---


**pyright打包:**

- `打包pyright`：由于是node项目，可以方便的使用pkg等工具进行可执行文件的生成，分别为windows，linux，macos生成了可执行文件


**pyright本地测试：**   
修改并使用 `./test.sh` 脚本进行本地测试开发


**工具使用教程：**   
> **请注意！！！**，使用 `pyright` 工具时，需要在环境变量中设置两个环境变量：
- `pyright_stubs_path` : 项目的存根文件夹，否则无法解析外部包的类型，请填写文件夹相对路径, 如 `projectName/stubs`, 填写 `stubs` 即可
- `pyright_python_version`: 项目所使用的python版本，请填写版本号 ，如 `3.8` ，不支持python2.x版本

以上两个变量可以在`分析方案`-`基础配置`-`环境变量`中填写，没有设置环境变量，工具将不会执行