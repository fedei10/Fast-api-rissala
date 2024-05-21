from fastapi import FastAPI, HTTPException
from models import UserCreate, Poster,LoginForm,subscriber,Post
from db import cursor, db
from passlib.context import CryptContext
import jwt
from fastapi.middleware.cors import CORSMiddleware
from mailer import send_mail
import json
from fastapi.responses import JSONResponse



app =FastAPI()
origins = ["*"]  

app.add_middleware(  
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],  
)
@app.get("/api/rissala/rissala.id")
async def get_postsbyId(id: int):

    query_posts = "SELECT * FROM posts WHERE id = %s;"
    cursor.execute(query_posts, (id,))
    posts_result = cursor.fetchall()
    

    if not posts_result:
        raise HTTPException(status_code=404, detail="Posts not found")
    else:
        return(posts_result)

#get all the posts from one creator
@app.get("/api/rissala/id")
async def get_posts(id_user: int):
    try:
        query_posts = "SELECT * FROM posts WHERE user_id = %s;"
        cursor.execute(query_posts, (id_user,))
        posts_result = cursor.fetchall()

        if not posts_result:
            raise HTTPException(status_code=404, detail="Posts not found")

        posts_with_keywords = []
        for post in posts_result:
            post_id = post[0]  # Assuming the first element of the tuple is the ID
            query_keywords = "SELECT keyword FROM keywords WHERE post_id = %s;"
            cursor.execute(query_keywords, (post_id,))
            keywords_result = cursor.fetchall()
            keywords_list = [kw[0] for kw in keywords_result]
            # Create Post instance with keywords
            post_model = Post(
                id=post_id,  # Assuming the first element is the ID
                title=post[1],  # Assuming the second element is the title
                post_img=post[2],  # Assuming the third element is the post_img
                user_id=post[3],  # Assuming the fourth element is the user_id
                content=post[4],
                style=post[5],
                category=post[6],
                keywords=keywords_list,

            )
            posts_with_keywords.append(post_model)

        return posts_with_keywords

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Delete a rissala by ID
@app.delete("/api/rissala/{post_id}", status_code=204)
async def delete_rissala(post_id: int):
    try:
        query = "DELETE FROM posts WHERE id = %s"
        cursor.execute(query, (post_id,))
        db.commit()
        query = "DELETE FROM keywords WHERE post_id = %s"
        cursor.execute(query, (post_id,))
        db.commit()
        return ("Rissala is Deleted successfully",post_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update a rissala by ID
@app.put("/api/rissala/update/{post_id}", status_code=200)
async def update_rissala(post_id: int, updated_rissala: Post):
    try:
        query = "UPDATE posts SET title = %s, content = %s, image = %s WHERE id = %s"
        cursor.execute(query, (updated_rissala.title, updated_rissala.content, updated_rissala.image, post_id))
        db.commit()
        return {"message": "Post updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#**************keywords****************
@app.post("/api/profil/post/keywords/", status_code=201)
async def add_keywords(id:int ,keyword:str):
    try:
        query = "SELECT * FROM keywords WHERE post_id = %s and keyword= %s ;"
        cursor.execute(query, (id, keyword))
        result = cursor.fetchall() 
        if result:
            return({"message": "Keyword already used"})
        else:
            try:
                query = "INSERT INTO keywords (post_id, keyword) VALUES (%s, %s)"
                cursor.execute(query, (id, keyword))
                db.commit()
                return {"message": "Keyword added succefully"}
            except Exception as e:
                return {str(e)}
    except Exception as e:
        return {str(e)}
@app.get("/api/profil/post/keywords/{id}")
async def show_keywords_post_id(id: int):
    query = "SELECT keyword FROM keywords WHERE post_id = %s AND keyword NOT LIKE '@%' AND keyword NOT LIKE '****@%' AND keyword NOT LIKE 'category@%';"
    cursor.execute(query, (id,))
    result = cursor.fetchall() 
    if result:
        return(result)
    else:
        return({"message": "No keywords ...yet!"})
@app.get("/api/profil/post/keywords/{keyword}")
async def show_post_id_keyword(keyword: str):
    query = "SELECT keyword FROM keywords WHERE keyword = %s;"
    cursor.execute(query, (keyword,))
    result = cursor.fetchall() 
    if result:
        return(result)
    else:
        return({"message": "No keywords ...yet!"})

@app.delete("/api/profil/post/keywords/delete")
async def delete_one_keyword(id: int, keyword: str):
    try:
        query = "DELETE FROM keywords WHERE post_id = %s AND keyword = %s;"
        cursor.execute(query, (id, keyword))
        deleted_rows = cursor.rowcount  # Get the number of rows deleted
        if deleted_rows > 0:
            return {"message": f"Deleted {deleted_rows} rows."}
        else:
            return {"message": "No rows deleted."}
    except Exception as e:
        print(f"Error deleting keyword: {e}")
        return {"message": "Delete operation failed."}

from collections import Counter

##########searchbar############

@app.get("/api/profil/post/SearchBar/")
async def searchPostByKeyword(keywords: str):
    try:

        # Split the input string of keywords into a list
        keyword_list = keywords.split()

        result_list = []
        for keyword in keyword_list:
            query = "SELECT post_id FROM keywords WHERE keyword LIKE %s;"
            cursor.execute(query, ('%' + keyword + '%',))
            result = cursor.fetchall()
            if result:
                post_ids = [row[0] for row in result]
                result_list.extend(post_ids)  # Extend the result_list with post_ids instead of appending a list

        # Count the occurrences of each post_id
        counter = Counter(result_list)

        # Create a list of unique post_ids sorted by their frequency (from most common to least common)
        unique_ordered_list = [element for element, count in counter.most_common()]

        return unique_ordered_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
@app.post("/api/users/", status_code=201)
async def create_user(user_data: UserCreate):
    try:
        query = "INSERT INTO creator (username, email, password, user_img) VALUES (%s, %s, %s ,%s)"
        cursor.execute(query, (user_data.username, user_data.email, user_data.password, user_data.user_img))
        db.commit()
        return {"message": "User created successfully"}
    except Exception as e:
        # Handle any database or other exceptions
        return {str(e)}

@app.get("/api/users/id")
async def connecter(id: int):
    try:
        query = "SELECT username,user_img,readings FROM creator WHERE id = %s;"
        cursor.execute(query, (id,))
        result = cursor.fetchone()  # Assuming you want to fetch one row
        if result:
            # Convert the fetched data into a dictionary with keys
            user_data = {
                "username": result[0],
                "user_img": result[1],
                "readings": result[2],
                "user_id":id
            }

            # Save the data to a JSON file
            with open('user_details.json', 'w') as json_file:
                json.dump(user_data, json_file)

            return JSONResponse(content=user_data)
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rissala/", status_code=201)
async def create_rissala(rissala: Poster):
    try:
        query = "INSERT INTO posts (title, post_img, user_id, content, style, category) VALUES (%s, %s, %s, %s, %s, %s);"
        cursor.execute(query, (rissala.title, rissala.post_img, rissala.user_id, rissala.content, rissala.style, rissala.category))
        db.commit()
        cursor.execute('SELECT email FROM subscribers where id=%s',(rissala.user_id,))
        emails = cursor.fetchall()
        email_list = [email[0] for email in emails]
        for i in email_list:
            send_mail(i,rissala.title,rissala.post_img,rissala.content,rissala.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        query = "SELECT id FROM posts WHERE title = %s AND post_img = %s AND user_id = %s AND content = %s AND style = %s;"
        cursor.execute(query, (rissala.title, rissala.post_img, rissala.user_id, rissala.content, rissala.style))
        last_id = cursor.fetchall()
        result_id = last_id[0]
        query = "SELECT username FROM creator WHERE id = %s;"
        cursor.execute(query, (rissala.user_id,))
        result_username = cursor.fetchone()
        if result_username:
            username_str = '@' + str(result_username[0])
            try:
                query = "INSERT INTO keywords (post_id, keyword) VALUES (%s, %s)"
                cursor.execute(query, (result_id[0], username_str))
                db.commit()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            word_list = '****@'+str(rissala.title)
            try:
                query = "INSERT INTO keywords (post_id, keyword) VALUES (%s, %s)"
                cursor.execute(query, (result_id[0], word_list))
                db.commit()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            cat = 'category@' + str(rissala.category)
            try:
                query = "INSERT INTO keywords (post_id, keyword) VALUES (%s, %s)"
                cursor.execute(query, (result_id[0], cat))
                db.commit()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
            return {"post_id": result_id[0] }
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/Login/")
async def Login(data:LoginForm):
    try:
        query="select email,password from creator where email= %s;"
        cursor.execute(query,(data.email,))
        row=cursor.fetchone()
        if(row and data.password!=row[1]):
            return{"message":"Wrong password"}
        
        elif(row and data.password==row[1]):
            token=auth(data.email,data.password)
            json=dict()
            json["message"]=token
            json["result"]=True
            return json
        elif(not row):
            return {"message":"Email not found"}

    except:
        return {"message": "login error"}


#token
def auth(email,password):
    data=dict()
    data[email]=str(password)
    secret_key="Zr78jAF_afZYYlbbixW66TmzkPqPUte5bZadr1kBz0s"
    algorithm = "HS256"
    encoded_jwt = jwt.encode(data, secret_key, algorithm=algorithm)
    return encoded_jwt


#Subs
@app.post("/api/profil/subscribe", status_code=201)
async def subscribe(subscriber: subscriber):
    query = "SELECT * FROM subscribers WHERE id = %s and email= %s;"
    cursor.execute(query, (subscriber.id, subscriber.email))
    result = cursor.fetchall() 
    if result:
        return({"message": "You are already subscribed to this creator"})
    else:
        try:
            query = "INSERT INTO subscribers (id, email) VALUES (%s, %s)"
            cursor.execute(query, (subscriber.id, subscriber.email))
            db.commit()
            return {"message": "Subscribed succefully"}
        except Exception as e:
            return {str(e)}

@app.get("/api/profil/subscribe/{id}")
async def show_subscribers(id: int):
    query = "SELECT email FROM subscribers WHERE id = %s;"
    cursor.execute(query, (id,))
    result = cursor.fetchall() 
    if result:
        return(result)
    else:
        return({"message": "No subscribers ...yet!"})



if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", port=8888, host='0.0.0.0', reload=True)