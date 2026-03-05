import matplotlib.pyplot as plt
import streamlit as st

def plot_bar(df, x, y, title, xlabel=None, ylabel=None, rotate=True):
    fig, ax = plt.subplots(figsize=(5,3.5))
    ax.bar(df[x], df[y])
    ax.set_title(title)
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y)
    if rotate:
        plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

def plot_line(df, x, y, title, xlabel=None, ylabel=None, rotate=True):
    fig, ax = plt.subplots(figsize=(5,3.5))
    ax.plot(df[x], df[y], marker="o")
    ax.set_title(title)
    ax.set_xlabel(xlabel or x)
    ax.set_ylabel(ylabel or y)
    if rotate:
        plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

def plot_pie(df, values, labels, title):
    fig, ax = plt.subplots(figsize=(5,3.5))
    ax.pie(df[values], labels=df[labels], autopct="%1.1f%%", startangle=140)
    ax.set_title(title)
    st.pyplot(fig)

def plot_stacked_bar(df, title, xlabel=None, ylabel=None, rotate=True):
    fig, ax = plt.subplots(figsize=(5,3.5))
    df.plot(kind='bar', stacked=True, ax=ax)

    ax.set_title(title)
    ax.set_xlabel(xlabel or df.index.name or "")
    ax.set_ylabel(ylabel or "")
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    if rotate:
        plt.xticks(rotation=45, ha="right")
    
    st.pyplot(fig)