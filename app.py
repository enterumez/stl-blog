import os
import sqlite3
import streamlit as st
import pandas as pd

# データベースファイルの名前
database = 'blog.db'

# データベースファイルが存在しない場合に作成
if not os.path.exists(database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        date DATE NOT NULL
    )
    ''')
    conn.commit()
    c.close()
    conn.close()

# 新しい投稿を追加する関数を定義します
def add_post(author, title, content, date):
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute('INSERT INTO posts (author, title, content, date) VALUES (?,?,?,?)', (author, title, content, date))
        conn.commit()
        c.close()
        conn.close()
    except sqlite3.Error as e:
        st.write(e)

# すべての投稿を取得する関数を定義します
def get_all_posts():
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute('SELECT * FROM posts')
        data = c.fetchall()
        c.close()
        conn.close()
        return data
    except sqlite3.Error as e:
        st.write(e)
        return []

# タイトルで投稿を取得する関数を定義します
def get_post_by_title(title):
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute('SELECT * FROM posts WHERE title=?', (title,))
        data = c.fetchone()
        c.close()
        conn.close()
        return data
    except sqlite3.Error as e:
        st.write(e)
        return None

# 投稿を削除する関数を定義します
def delete_post(title):
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute('DELETE FROM posts WHERE title=?', (title,))
        conn.commit()
        c.close()
        conn.close()
    except sqlite3.Error as e:
        st.write(e)

# Define some HTML templates for displaying the posts
title_temp = """
<div style="background-color:#464e5f;padding:10px;border-radius:10px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h4>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
<h6>Author: {}</h6>
<br/>
<br/>
<p style="text-align:justify"> {}</p>
</div>
"""

post_temp = """
<div style="background-color:#464e5f;padding:10px;border-radius:5px;margin:10px;">
<h4 style="color:white;text-align:center;">{}</h4>
<h6>Author: {}</h6>
<h6>Date: {}</h6>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;width: 50px;height: 50px;border-radius: 50%;">
<br/>
<br/>
<p style="text-align:justify"> {}</p>
</div>
"""

# Create a sidebar menu with different options
menu = ["Home", "View Posts", "Add Post", "Search", "Manage"]
choice = st.sidebar.selectbox("Menu", menu)

# Display the selected option
if choice == "Home":
    st.title("Welcome to my blog")
    st.write("This is a simple blog app built with streamlit and python.")
    st.write("You can view, add, search, and manage posts using the sidebar menu.")
    st.write("Enjoy!")
elif choice == "View Posts":
    st.title("View Posts")
    st.write("Here you can see all the posts in the blog.")
    posts = get_all_posts()
# Display each post as a card
for i, post in enumerate(posts):
    st.markdown(title_temp.format(post[1], post[0], post[2][:50] + "..."), unsafe_allow_html=True)
    if st.button(f"Read More###{i}", key=post[1]):
        st.markdown(post_temp.format(post[1], post[0], post[3], post[2]), unsafe_allow_html=True)

elif choice == "Add Post":
    st.title("Add Post")
    st.write("Here you can add a new post to the blog.")
    with st.form(key="add_form"):
        author = st.text_input("Author")
        title = st.text_input("Title")
        content = st.text_area("Content")
        date = st.date_input("Date")
        submit = st.form_submit_button("Submit")
    if submit:
        add_post(author, title, content, date)
        st.success("Post added successfully")
elif choice == "Search":
    st.title("Search")
    st.write("Here you can search for a post by title or author.")
    query = st.text_input("Enter your query")
    if query:
        posts = get_all_posts()
        results = [post for post in posts if query.lower() in post[0].lower() or query.lower() in post[1].lower()]
        if results:
            st.write(f"Found {len(results)} matching posts:")
            for result in results:
                st.markdown(title_temp.format(result[1], result[0], result[2][:50] + "..."), unsafe_allow_html=True)
                if st.button("Read More", key=result[1]):
                    st.markdown(post_temp.format(result[1], result[0], result[3], result[2]), unsafe_allow_html=True)
        else:
            st.write("No matching posts found")
elif choice == "Manage":
    st.title("Manage")
    st.write("Here you can delete posts or view some statistics.")
    titles = [post[1] for post in get_all_posts()]
    title = st.selectbox("Select a post to delete", titles)
    if st.button("Delete"):
        delete_post(title)
        st.success("Post deleted successfully")
    if st.checkbox("Show statistics"):
        posts = get_all_posts()
        df = pd.DataFrame(posts, columns=["author", "title", "content", "date"])
        st.write("Number of posts:", len(posts))
        st.write("Number of authors:", len(df["author"].unique()))
        st.write("Most recent post:", df["date"].max())
        st.write("Oldest post:", df["date"].min())
        st.write("Posts by author:")
        author_count = df["author"].value_counts()
        st.bar_chart(author_count)
