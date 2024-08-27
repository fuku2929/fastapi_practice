from fastapi import FastAPI, Query, Path, Body, Header
from enum import Enum
from typing import Union, List, Set
from pydantic import BaseModel, HttpUrl

class ModelName(str, Enum):
# strとEnumを継承したサブクラス
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"
    # 固定値のクラス属性

class Image(BaseModel):
    url: HttpUrl
    name: str

class Item(BaseModel):
# データモデルの宣言
    name:str = None
    description: Union[str, None] = None
    price: float = None
    tax: Union[float, None] = None
    tags: List[str] = []
    item: Union[List[Image], None] = None

class User(BaseModel):
    username: str
    full_name: Union[str, None] = None
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "Foo",
                    "full_name": "Foo Bar",
                }
            ]
        }
    }

app = FastAPI() 
# app is an instance of FastAPI

@app.post("/items/")
async def create_item(item: Item):
    return item
# 使い方？

@app.get("/items/head")
async def read_items(user_agent: Union[str, None]= Header(default=None)):
    return {"User-Agent": user_agent}

@app.get("/")
async def read_root():
# パスオペレーション関数
    return {"Hello": "World"}

@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int = Path(title="The ID of the item to get", ge=0, le=1000), 
    item: Union[Item, None] = None,
    q: Union[str, None] = None
    ):
    return {"item_id": item_id, **item.dict()}

@app.put("/items/{bodyitem_id}")
async def body_update_item(bodyitem_id: int, bodyitem: Item, user: User, importance: int = Body()):
    results = {"bodyitem_id": bodyitem_id, "bodyitem": bodyitem, "user": user, "importance": importance}
    return results

@app.get("/users/{user_id}/items/{item_id}")
async def read_item(
    user_id: int, item_id: str, q: Union[str, None] = None, short: bool = False
    ):
    item = {"item_id": item_id,"owner_id": user_id}
    if q:
        return item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

@app.get("/items/{item_id}")
async def read_user_item(*, item_id: int = Path(title="The ID of the item to get", ge=0, le=1000)):
    item = {"item_id": item_id}
    return item

@app.get("/items/")
async def read_items(q: Union[List[str], None] = Query(default=["foo", "bar"])):
    query_items = {"q": q}
    return query_items


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
# 作成したenumクラスであるModelNameを使用した型アノテーションを持つパスパラメータ　Enum...列挙型

    if model_name is ModelName.alexnet:
    # Enumクラスのインスタンスは、他のEnumクラスのインスタンスと比較できる

        return {"model_name": model_name, "message": "Deep learnign FTW!"}
    if model_name.value == "lenet":
    # .valueとつけることで、実際の値と比較できる

        return {"model_name" : model_name, "message": "LeCNN all the images"}
    
    return {"model_name": model_name, "message": "Have some residuals"}
    # これなに？どういう時に出てくるんだろうか

@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
