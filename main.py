import asyncio
from datetime import datetime

# import sqlalchemy
from aiohttp import ClientSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, JSON
# from sqlalchemy import String as String


from more_itertools import chunked

CHUNK_SIZE = 15
PERSON_COUNT = 85

PG_DSN = 'postgresql+asyncpg://erashov:1234@127.0.0.1:5431/asyncio_db'
engine = create_async_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

swapi_url = 'https://swapi.dev/api/people/'
ext_list = [
    {'ext_type': 'films', 'ext_name': 'title'}, 
    {'ext_type': 'species', 'ext_name': 'name'}, 
    {'ext_type': 'vehicles', 'ext_name': 'name'}, 
    {'ext_type': 'starships', 'ext_name': 'name'}
    ]
hash_ext_dict = {}


class People(Base):
    __tablename__ = 'people'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    birth_year = Column(String)
    gender = Column(String)
    height = Column(String)
    mass = Column(String)
    eye_color = Column(String)
    hair_color = Column(String)
    skin_color = Column(String)
    species = Column(String)
    homeworld = Column(String)
    starships = Column(String)
    vehicles = Column(String)
    films = Column(String)



async def chunk_async(iter, chank_size):

    buffer = []
    while True:
        try:
            res = await iter.__anext__()
        except StopAsyncIteration:
            break

        buffer.append(res)
        if len(buffer) == chank_size:
            yield buffer
            buffer = []


async def get_person(person_id: int, session: ClientSession):
    print(f"upload people {person_id}")
    async with session.get(f'{swapi_url}{person_id}') as resp:
        json_data = await resp.json()

    for ext_dict in ext_list:
        ext_key = ext_dict['ext_type']
        extension = json_data.get(ext_key)
        ext_type = ext_dict['ext_name']
        if extension:
            coro_ext = [get_extention(extensions=ext, ext_type=ext_type, session=session) for ext in extension]
            ext_result = await asyncio.gather(*coro_ext)
            json_data[ext_key] = ', '.join(ext_result)
        else:
            json_data[ext_key] = None

    print(f'end upload {person_id}')
    return json_data


async def get_people():
    async with ClientSession() as session:
        for chunk in chunked(range(1, PERSON_COUNT), CHUNK_SIZE):
            coro = [get_person(person_id=i, session=session) for i in chunk]
            res = await asyncio.gather(*coro)
            for item in res:
                print(item)
                yield item


async def get_extention(extensions, ext_type: str, session: ClientSession):
    print(f'begin {extensions}')
    ext_hash = hash(extensions)
    if ext_hash in hash_ext_dict:
        print("well done!", hash_ext_dict[ext_hash])
        result = hash_ext_dict[ext_hash]
    else:
        async with session.get(f'{extensions}') as resp:
            json_data = await resp.json()
        print(f'end {extensions}')
        result = json_data[ext_type]
        hash_ext_dict[ext_hash] = result
    return result


async def ins_people(people_chunk):
    async with Session() as session:
        session.add_all([People(**{x: item[x] for x in (
            'id', 'name', 'height', 'mass', 'hair_color', 'skin_color', 'eye_color', 'birth_year',
            'gender', 'homeworld', 'films', 'species', 'vehicles', 'starships'
                )
                  if x in item}) for item in people_chunk])
        await session.commit()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

    async for chunk in chunk_async(get_people(), CHUNK_SIZE):
        asyncio.create_task(ins_people(chunk))

    tasks = set(asyncio.all_tasks()) - {asyncio.current_task()}

    for task in tasks:
        await task



if __name__ == '__main__':
    start = datetime.now()
    asyncio.run(main())
    print(datetime.now() - start)
