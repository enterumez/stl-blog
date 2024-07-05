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
        c.execute('''
        INSERT INTO posts (author, title, content, date)
        SELECT ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM posts WHERE author = ? AND title = ? AND content = ? AND date = ?
        )
        ''', (author, title, content, date, author, title, content, date))
        conn.commit()
        c.close()
        conn.close()
        st.success("Post added successfully")
    except sqlite3.Error as e:
        st.error(f"Error adding post: {e}")

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
        st.error(f"Error fetching posts: {e}")
        return []

# 特定の投稿をIDで取得する関数を定義します
def get_post_by_id(post_id):
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute('SELECT * FROM posts WHERE id=?', (post_id,))
        data = c.fetchone()
        c.close()
        conn.close()
        return data
    except sqlite3.Error as e:
        st.error(f"Error fetching post: {e}")
        return None

# 投稿を更新する関数を定義します
def update_post(post_id, author, title, content, date):
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute('''
        UPDATE posts
        SET author=?, title=?, content=?, date=?
        WHERE id=?
        ''', (author, title, content, date, post_id))
        conn.commit()
        c.close()
        conn.close()
        st.success("Post updated successfully")
    except sqlite3.Error as e:
        st.error(f"Error updating post: {e}")

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
    # Display each post with update and read more buttons
    for i, post in enumerate(posts):
        st.markdown(title_temp.format(post[1], post[0], post[3], post[2][:50] + "..."), unsafe_allow_html=True)
        # Add a button to view the full post
        read_more_button_key = f"read_more_{post[0]}"  # Generate a unique key here
        if st.button("Read More", key=read_more_button_key):
            st.markdown(post_temp.format(post[1], post[0], post[3], post[2]), unsafe_allow_html=True)
        # Add a button to update the post
        update_button_key = f"update_post_{post[0]}"  # Generate a unique key here
        if st.button("Update", key=update_button_key):
            # Show form to update post
            with st.form(key=f"update_form_{post[0]}"):
                author = st.text_input("Author", value=post[1])
                title = st.text_input("Title", value=post[2])
                content = st.text_area("Content", value=post[3])
                submit = st.form_submit_button("Submit")
            if submit:
                update_post(post[0], author, title, content)
                st.experimental_rerun()  # 更新後にアプリを再読み込みするためにrerunを使用
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
                read_more_button_key = f"read_more_{result[0]}"  # Generate a unique key here
                if st.button("Read More", key=read_more_button_key):
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
