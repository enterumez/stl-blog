
import os
import streamlit as st
import sqlite3
import pandas as pd

# データベースファイルの名前
database = 'blog.db'

# SQLiteデータベースに接続（データベースが存在しない場合は新規作成されます）
conn = sqlite3.connect(database)

# カーソルオブジェクトを作成する
c = conn.cursor()

# テーブルを作成する（例として）
c.execute('CREATE TABLE IF NOT EXISTS posts (author TEXT NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL, date DATE NOT NULL)')

# カーソルを閉じる
c.close()

# 接続を閉じる
conn.close()

# 新しい投稿を追加する関数を定義します
def add_post(author, title, content, date):
    try:
        # データベースに接続します
        conn = sqlite3.connect(database)
        # カーソルオブジェクトを作成します
        c = conn.cursor()
        # posts テーブルに新しい行を挿入します
        c.execute('INSERT INTO posts (author, title, content, date) VALUES (?,?,?,?)', (author, title, content, date))
        # 変更をデータベースに保存します
        conn.commit()
        # カーソルと接続を閉じます
        c.close()
        conn.close()
    except sqlite3.Error as e:
        # エラーメッセージを表示します
        print(e)

# すべての投稿を取得する関数を定義します
def get_all_posts():
    try:
        # データベースに接続します
        conn = sqlite3.connect(database)
        # カーソルオブジェクトを作成します
        c = conn.cursor()
        # posts テーブルからすべての行を選択します
        c.execute('SELECT * FROM posts')
        # すべての結果を取得します
        data = c.fetchall()
        # カーソルと接続を閉じます
        c.close()
        conn.close()
        # データを返します
        return data
    except sqlite3.Error as e:
        # エラーメッセージを出力します
        print(e)

# タイトルで投稿を取得する関数を定義します
def get_post_by_title(title):
    try:
        # データベースに接続します
        conn = sqlite3.connect(database)
        # カーソルオブジェクトを作成します
        c = conn.cursor()
        # タイトルに一致する posts テーブルから行を選択します
        c.execute('SELECT * FROM posts WHERE title=?', (title,))
        # 結果を取得します
        data = c.fetchone()
        # カーソルと接続を閉じます
        c.close()
        conn.close()
        # データを返します
        return data
    except sqlite3.Error as e:
        # エラーメッセージを出力します
        print(e)

# 投稿を削除する関数を定義します
def delete_post(title):
    try:
        # データベースに接続します
        conn = sqlite3.connect(database)
        # カーソルオブジェクトを作成します
        c = conn.cursor()
        # タイトルに一致する posts テーブルから行を削除します
        c.execute('DELETE FROM posts WHERE title=?', (title,))
        # 変更をデータベースに保存します
        conn.commit()
        # カーソルと接続を閉じます
        c.close()
        conn.close()
    except sqlite3.Error as e:
        # エラーメッセージを表示します
        print(e)

# 関数をテストする
add_post('Alice', 'Hello World', 'This is my first post', '2021-01-01')
add_post('Bob', 'Streamlit Rocks', 'This is my second post', '2021-01-02')
add_post('Charlie', 'Python is Awesome', 'This is my third post', '2021-01-03')
print(get_all_posts())
print(get_post_by_title('Streamlit Rocks'))
delete_post('Hello World')
print(get_all_posts())

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
    # Get all the posts from the database
    posts = get_all_posts()
    # Display each post as a card
    for post in posts:
        st.markdown(title_temp.format(post[1], post[0], post[2][:50] + "..."), unsafe_allow_html=True)
        # Add a button to view the full post
        if st.button("Read More", key=post[1]):
            st.markdown(post_temp.format(post[1], post[0], post[3], post[2]), unsafe_allow_html=True)
elif choice == "Add Post":
    st.title("Add Post")
    st.write("Here you can add a new post to the blog.")
    # Create a form to get the post details
    with st.form(key="add_form"):
        author = st.text_input("Author")
        title = st.text_input("Title")
        content = st.text_area("Content")
        date = st.date_input("Date")
        submit = st.form_submit_button("Submit")
    # If the form is submitted, add the post to the database
    if submit:
        add_post(author, title, content, date)
        st.success("Post added successfully")
elif choice == "Search":
    st.title("Search")
    st.write("Here you can search for a post by title or author.")
    # Create a text input to get the search query
    query = st.text_input("Enter your query")
    # If the query is not empty, search for the matching posts
    if query:
        # Get all the posts from the database
        posts = get_all_posts()
        # Filter the posts by the query
        results = [post for post in posts if query.lower() in post[0].lower() or query.lower() in post[1].lower()]
        # Display the results
        if results:
            st.write(f"Found {len(results)} matching posts:")
            for result in results:
                st.markdown(title_temp.format(result[1], result[0], result[2][:50] + "..."), unsafe_allow_html=True)
                # Add a button to view the full post
                if st.button("Read More", key=result[1]):
                    st.markdown(post_temp.format(result[1], result[0], result[3], result[2]), unsafe_allow_html=True)
        else:
            st.write("No matching posts found")
elif choice == "Manage":
    st.title("Manage")
    st.write("Here you can delete posts or view some statistics.")
    # Create a selectbox to choose a post to delete
    titles = [post[1] for post in get_all_posts()]
    title = st.selectbox("Select a post to delete", titles)
    # Add a button to confirm the deletion
    if st.button("Delete"):
        delete_post(title)
        st.success("Post deleted successfully")
    # Create a checkbox to show some statistics
    if st.checkbox("Show statistics"):
        # Get all the posts from the database
        posts = get_all_posts()
        # Convert the posts to a dataframe
        df = pd.DataFrame(posts, columns=["author", "title", "content", "date"])
        # Display some basic statistics
        st.write("Number of posts:", len(posts))
        st.write("Number of authors:", len(df["author"].unique()))
        st.write("Most recent post:", df["date"].max())
        st.write("Oldest post:", df["date"].min())
        # Display a bar chart of posts by author
        st.write("Posts by author:")
        author_count = df["author"].value_counts()
        st.bar_chart(author_count)
