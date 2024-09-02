from fastapi import FastAPI, Query, Path, Body, Header, status, Form, HTTPException
from enum import Enum
from typing import Dict, Union, List, Set
from pydantic import BaseModel, HttpUrl, EmailStr
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from fastapi.encoders import jsonable_encoder

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

class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: Union[str, None] = None

class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: Union[str, None] = None

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    full_name: Union[str, None] = None

def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password

def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db

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
    
# 重複の削減Tips
class ItemBase(BaseModel):
    description: str
    price: float
    tax: float = 10.5

class ItemIn(ItemBase):
    passwoed: str

class ItemOut(ItemBase):
    pass

class ItemDB(ItemBase):
    hashed_password: str

class CarItem(ItemBase):
    type: str = "car"

class PlaneItem(ItemBase):
    type: str = "plane"
    size: int


app = FastAPI() 
# app is an instance of FastAPI

@app.get("/keyword-weights/", response_model = Dict[str, float])
async def read_keyword_weights():
    return {"foo": 2.3, "bar": 3.4}

@app.post("/items/", response_model = Item, status_code = status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item
# 使い方？



@app.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}


@app.post("/user/", response_model=UserOut, response_model_exclude_unset=True)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved

@app.get("/items/head")
async def read_items(user_agent: Union[str, None]= Header(default=None)):
    return {"User-Agent": user_agent}

@app.get("/item/{item_type}", response_model=Union[CarItem, PlaneItem])
async def read_item(item_type: str):
    return item_type

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

fake_db = {}

@app.put("ite/{id}")
async def update_item(id: str, item: Item):
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data

print(fake_db)

items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The Bar fighters", "price": 62, "tax": 20.2},
    "baz": {
        "name": "Baz",
        "description": "There goes my baz",
        "price": 50.2,
        "tax": 10,
    },
    "fo": 12,
}
goods = [
    {"name": "Foo", "description": "There comes my hero"},
    {"name": "Red", "description": "It's my aeroplane"},
]
@app.get(
    "/items/{item_id}/name",
    response_model=Item,response_model_include={'name', 'description'})
# internal server errorが出てしまう...なぜ...
async def read_item_name(item_id: str):
    return items


@app.get("/items/{item_id}/name", response_model_include={'name', 'description'})
async def read_item_name(item_id: str):
    return items

@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude={"tax"})
async def read_item_public_data(item_id):
    return items
    # item[item_id]とするとエラーになる

@app.get("goods/{good_id}", response_model=List[Item])
async def read_good():
    return goods

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
async def read_user_item(*, item_id:str):
    item = {"item_id": item_id}
    if item_id not in items:
        raise HTTPException(status_code=404, detail="item not found")
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

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)
