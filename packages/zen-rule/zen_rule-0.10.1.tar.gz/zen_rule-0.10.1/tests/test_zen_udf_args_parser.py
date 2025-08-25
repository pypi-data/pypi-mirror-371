
#  pytest tests/zen/test_zen.py -sl
#  -s 捕获标准输出
#  -l 显示出错的测试用例中的局部变量
#  -k 指定某一个测试用例执行
#  --setup-show  展示的单元测试 SETUP 和 TEARDOWN 的细节，展示测试依赖的加载和销毁顺序

import asyncio
import json
import logging
from pathlib import Path
from pprint import pprint
import uuid
import pytest
import zen
from zen_rule import ZenRule

logger = logging.getLogger(__name__)

graphjson = """
{
  "contentType": "application/vnd.gorules.decision",
  "nodes": [
    {
      "id": "115975ef-2f43-4e22-b553-0da6f4cc7f68",
      "type": "inputNode",
      "position": {
        "x": 180,
        "y": 240
      },
      "name": "Request"
    },
    {
      "id": "138b3b11-ff46-450f-9704-3f3c712067b2",
      "type": "customNode",
      "position": {
        "x": 470,
        "y": 240
      },
      "name": "customNode1",
      "content": {
        "kind": "sum",
        "config": {
          "version": "v3",
          "meta": {
            "user": "wanghao@geetest.com",
            "proj": "proj_id"
          },
          "prop1": "{{ a + 10 }}",
          "passThrough": true,
          "inputField": null,
          "outputPath": null,
          "expressions": [
            {
              "id": "52d41e3d-067d-4930-89bd-832b038cd08f",
              "key": "result",
              "value": "foo;;myvar ;;max([5, 8, 2, 11, 7]);;rand(100);; 'fccd;;jny' ;;3+4"
            }
          ]
        }
      }
    },
    {
      "id": "db8797b1-bcc1-4fbf-a5d8-e7d43a181d5e",
      "type": "outputNode",
      "position": {
        "x": 780,
        "y": 240
      },
      "name": "Response"
    }
  ],
  "edges": [
    {
      "id": "05740fa7-3755-4756-b85e-bc1af2f6773b",
      "sourceId": "115975ef-2f43-4e22-b553-0da6f4cc7f68",
      "type": "edge",
      "targetId": "138b3b11-ff46-450f-9704-3f3c712067b2"
    },
    {
      "id": "5d89c1d6-e894-4e8a-bd13-22368c2a6bc7",
      "sourceId": "138b3b11-ff46-450f-9704-3f3c712067b2",
      "type": "edge",
      "targetId": "db8797b1-bcc1-4fbf-a5d8-e7d43a181d5e"
    }
  ]
}
"""

graphs = {"udf.json": graphjson}


def loader(key):

    _graph =  graphs[key]
    return _graph


def udf_args_helper(graph):
    graph = json.loads(graph)
    for node in graph["nodes"]:
        if node["type"] == "customNode":
          udf_expressions = node["content"]["config"]["expressions"]
          udf_expr = {
            "id": str(uuid.uuid4()),
            "key": "result",
            "value": "foo;;literal_args"
          }
          udf_expressions = [udf_expr]
    
    return json.dumps(graph)


async def test_zenrule():
    """
        推荐线上生产环境使用此模式进行规则执行, 可以缓存决策对象, 提高性能.
    """
    zr = ZenRule({})
    # 测试的规则图写在了代码中.
    # basedir = Path(__file__).parent
    # filename = basedir / "graph" / "custom_v3.json"
    key = "udf.json"

    ## 读取 standard.csv 中的数据, 其中第一列数据当做udf的字面输入量参数, 第二列数据当做此自定义节点的输入
    
    if not zr.get_decision_cache(key):
        content = udf_args_helper(graphjson)
        zr.create_decision_with_cache_key(key, content)  # 将规则图缓存在键下, 这样可以只读取规则一次，解析一次，然后复用决策对象 decision
    result = await zr.async_evaluate(key, {"input": 7, "myvar": 15})
    print("zen rule custom_v3 result:", result)