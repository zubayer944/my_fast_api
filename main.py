from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from starlette.responses import Response
import psycopg2
from psycopg2.extras import RealDictCursor
import time

from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

# instans of the fast api
app = FastAPI()


# post model
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


# make connection to the database
# try  to connect to thr database untill its got connected
# to the databse
while True:
    try:
        connection = psycopg2.connect(
            host='localhost',
            database='jubayerDb',
            user='postgres',
            password='123456',
            cursor_factory=RealDictCursor
        )

        cursor = connection.cursor()

        print('-> Database connected successfully! <-')
        break

    except Exception as error:
        time.sleep(2)
        print('-> Filed to connect to the database <-')
        print('-> Error: ', error)


# return all posts from POSTS table
@app.get('/get-all-posts')
def get_all_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts_list = cursor.fetchall()
    return posts_list
#
# create a post entry to database
@app.post('/create-post', status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s)
    RETURNING *""",
                   (post.title, post.content, post.published)
                   )

    newly_created_post = cursor.fetchone()

    connection.commit()

    return newly_created_post


# return all posts from POSTS table
@app.get('/get-all-posts')
def get_all_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts_list = cursor.fetchall()
    return posts_list


# return a specific post from database
@app.get('/get-post-by-id/{post_id}')
def get_post_by_id(post_id: int):
    cursor.execute(
        """SELECT * FROM posts WHERE id = %s""", (str(post_id)),
    )

    fetched_post = cursor.fetchone()

    if not fetched_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'the post with id = {post_id} not found'
        )

    return {'data': fetched_post}


# delete an post from datbase by post id
@app.delete('/delete-post/{post_id}', status_code=HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    cursor.execute(
        """DELETE FROM posts WHERE id = %s RETURNING *""",
        (str(post_id))
    )

    deleted_post = cursor.fetchone()

    if not deleted_post:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f'Delete operation failed because the post with id = {post_id} not fount'
        )

    return Response(status_code=HTTP_204_NO_CONTENT)


# edit post
@app.put('/update-post/{post_id}')
def update_post(post_id: int, post: Post):
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
        (post.title, post.content, post.published, str(post_id))
    )

    updated_post = cursor.fetchone()

    connection.commit()

    if not updated_post:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f'post with id = {post_id} not found to update'
        )

    return {'data': updated_post}
