from typing import Any
import asyncio
import httpx
from urllib.parse import quote
from mcp.server.fastmcp import FastMCP
import dotenv
import os

# Initialize FastMCP server
mcp = FastMCP("BB-MCP")

# Constants
dotenv.load_dotenv()
BB_BASE_URL = os.getenv("BB_BASE_URL")
USER_AGENT = "CUHKSZ-bb-mcp-app/1.0"

async def make_search_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Server with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_courses(result: dict[str, Any]) -> str:
    """Format an result into a readable string."""
    return f"""
Title: {result.get('title', 'Unknown')}
Code: {result.get('code', 'Unknown')}
Instructor: {result.get('instructor', 'Unknown')}
ID: {result.get('id', 'Unknown')}
"""

def format_todo(result: dict[str, Any]) -> str:
    """Format a todo result into a readable string."""
    return f"""
Summary: {result.get('summary', 'Unknown')}
Link: {result.get('link', 'Unknown')}
Start: {result.get('dtstart', 'Unknown')}
End: {result.get('dtend', 'Unknown')}
"""

def format_announcement(result: dict[str, Any]) -> str:
    """Format an announcement result into a readable string."""
    return f"""
Title: {result.get('title', 'Unknown')}
Poster: {result.get('poster', 'Unknown')}
Time: {result.get('time', 'Unknown')}
Detail: {result.get('detail', 'Unknown')}
"""

def format_grade(result: dict[str, Any]) -> str:
    """Format a grade result into a readable string."""
    return f"""
Title: {result.get('title', 'Unknown')}
Grade: {result.get('grade', 'Unknown')}
Max Point possible: {result.get('max_grade', 'Unknown')}
Average: {result.get('average', 'Unknown')}
Median: {result.get('median', 'Unknown')}
Date: {result.get('date', 'Unknown')}
"""


@mcp.tool()
async def fetch_course_list() -> str:
    """Get user's enrolled course list from CUHKSZ.
    Returns:
        basic course information including course name, code, and instructor.
    """
    url = f"{BB_BASE_URL}/courses"
    data = await make_search_request(url)
    if not data:
        return "Unable to fetch courses."
    results = [format_courses(result) for result in data]
    return "\n---\n".join(results)

@mcp.tool()
async def fetch_todo() -> str:
    """Get user's todo list from CUHKSZ.
    Returns:
        basic todo information including summary, link, start time, and end time.
    Tips:
        You can hide access links using markdown syntax:[text](link)
        you need to remind user that these links are not accessible before
        user login bb on their own browser.

    """
    url = f"{BB_BASE_URL}/todo"
    data = await make_search_request(url)
    results = [format_todo(result) for result in data]
    return "\n---\n".join(results) if results else "\n---\nNo todo items found. You are all set!"

@mcp.tool()
async def fetch_announcements(code: str, num: int = None) -> str:
    """Get user's announcements from CUHKSZ.
    Args:
        code: course code to filter announcements. e.g MAT3007
        (Optional) num: number of announcements to fetch(from latest to oldest).
            If not specified, all announcements will be fetched.
    Returns:
        basic announcement information including title, poster, time, and detail.
    """
    url = f"{BB_BASE_URL}/announcements?code={code}&num={num}" if num else f"{BB_BASE_URL}/announcements?code={code}"
    data = await make_search_request(url)
    results = [format_announcement(result) for result in data]
    return "\n---\n".join(results) if results else "\n---\nNo announcements found."

@mcp.tool()
async def fetch_grades(code: str) -> str:
    """Get user's grades from CUHKSZ.
    Args:
        code: course code to filter grades. e.g MAT3007
    Returns:
        basic grade information including title, grade, max grade, average, median, and date.
    """
    url = f"{BB_BASE_URL}/grades?code={code}"
    data = await make_search_request(url)
    results = [format_grade(result) for result in data]
    return "\n---\n".join(results) if results else "\n---\nNo grades found."

@mcp.tool()
async def send_email(body: str, subject: str, receiver_email: str, receiver_name: str) -> str:
    """Send email.
    Args:
        body: email body (support html format) e.g. '<h2> The grades for MAT3007 are out... </h2>'
        subject: email subject e.g. 'Grades for MAT3007'
        receiver_email: email receiver e.g. 'abc123@gmail.com'
        receiver_name: email receiver name e.g. 'Ming Wen'
    Returns:
        'Email sent successfully!' if success
        'Failed to send email.' if failed.
    """
    url = f"{BB_BASE_URL}/email"
    data = {
        "body": body,
        "subject": subject,
        "receiver_email": receiver_email,
        "receiver_name": receiver_name,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, timeout=30.0)
            response.raise_for_status()
            return response.text
        except Exception:
            return "Failed to send email."
    
@mcp.tool()
async def fetch_content(code: str, verbose: bool = False) -> str:
    """Get course content from CUHKSZ.
    Args:
        code: course code to filter content. e.g MAT3007
        verbose: whether to return detailed content information.
    Returns:
        basic content information including title, type, and link.
    """
    if verbose:
        url = f"{BB_BASE_URL}/content?code={code}"
    else:
        url = f"{BB_BASE_URL}/content/tree?code={code}"
        print(url)
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/plain"
        }
        # todo
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                result = response.text  # 注意：没有括号！
                print(result)
            except Exception as e:
                print(f"Error: {e}")
                result = ""
        return "\n---\n" + result
    
    return "\n---\n".join(result)

@mcp.tool()
async def find_content_detail(code: str, folder: str, content: str) -> str:
    """Find content in course.
    Args:
        code: course code to filter content. e.g MAT3007
        folder: content's father folder name to filter content. e.g. homework
        content: content name to filter content. e.g. hw1
    Returns:
        basic content information including title, type, and link.
    Hints: You can use tool 'fetch_content' to get the content tree to know where to search.
    """
    url = f"{BB_BASE_URL}/content/find"
    data = {
        "code": code,
        "folder": folder,
        "content": content,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=data, timeout=30.0)
            response.raise_for_status()
            result = response.text  # 注意：没有括号！
        except Exception as e:
            result = f"Error: {e}"
    return "\n---\n" + result

@mcp.tool()
async def download_file(url: str, name: str, download_dir: str | os.PathLike = ".") -> str:
    """Download file from url.
    Args:
        url: file url to download
        name: file name to save
        download_dir: directory to save file (recommend to use absolute path)
    Returns:
        'File downloaded successfully!' if success
        'Failed to download file.' if failed.
    Hints: You can use tool 'fetch_content' to get the content tree to know where to search.
        Then you can use tool 'find_content_detail' to find the content you want.
        for file content with link(e.g. https://bb.cuhk.edu.cn/bbcswebdav/pid-539547-dt-content-rid-10064341_1/
        xid-10064341_1) and file name(e.g. exam_sample_final_solution_mopt_25.pdf),
        you can use tool 'download_file' to download the file.
    """
    post_url = f"{BB_BASE_URL}/download"
    data = {
        "url": url,
        "name": name,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(post_url, json=data, timeout=30.0)
            response.raise_for_status()
            with open(name, "wb") as f:
                f.write(response.content)
            return "File downloaded successfully!"
        except Exception as e:
            print(f"Error: {e}")
            return "Failed to download file."


async def test():
    print("BB_BASE_URL: ", BB_BASE_URL)
    while True:
        print("\n请选择要测试的功能：")
        print("1. 获取内容 (find_content_detail)")
        print("2. 下载文件 (download_file)")
        print("3. 获取内容 (fetch_content)")
        print("4. 获取成绩 (fetch_grades)")
        print("0. 退出")
        choice = input("输入选项编号: ").strip()
        if choice == "1":
            code = input("请输入课程代码 (如 MAT3007): ").strip()
            folder = input("请输入文件夹名称 (如 Notebook): ").strip()
            content = input("请输入内容名称 (如 Notebook: Week 01): ").strip()
            result = await find_content_detail(code, folder, content)
            print("结果：\n", result)
        elif choice == "2":
            url = input("请输入文件下载链接: ").strip()
            name = input("请输入保存的文件名: ").strip()
            download_dir = input("请输入保存目录（默认当前目录，直接回车即可）: ").strip()
            if not download_dir:
                download_dir = "."
            result = await download_file(url, name, download_dir)
            print("结果：\n", result)
        elif choice == "3":
            code = input("请输入课程代码 (如 MAT3007): ").strip()
            result = await fetch_content(code)
            print("结果：\n", result)
        elif choice == "4":
            code = input("请输入课程代码 (如 MAT3007): ").strip()
            result = await fetch_grades(code)
            print("结果：\n", result)
        elif choice == "0":
            print("退出测试。")
            break
        else:
            print("无效选项，请重新输入。")

if __name__ == "__main__":
    dotenv.load_dotenv()
    asyncio.run(test())