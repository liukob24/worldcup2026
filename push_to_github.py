#!/usr/bin/env python3
"""
GitHub推送脚本 - 将analysis.json推送到GitHub
"""
import json
import base64
import requests
import os

# GitHub配置
REPO_OWNER = "liukob24"
REPO_NAME = "worldcup2026"
BRANCH = "main"
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def push_to_github():
    """推送analysis.json到GitHub"""
    # 读取本地analysis.json
    with open('data/analysis.json', 'rb') as f:
        content = f.read()
    
    # Base64编码
    content_base64 = base64.b64encode(content).decode('utf-8')
    
    # GitHub API - 获取当前文件的SHA
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/data/analysis.json"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 获取当前文件SHA
    response = requests.get(url, headers=headers)
    sha = None
    if response.status_code == 200:
        sha = response.json().get('sha')
        print(f"获取到当前文件SHA: {sha}")
    else:
        print(f"获取SHA失败: {response.status_code}")
    
    # 准备提交数据
    commit_data = {
        "message": "🤖 赛前24小时分析更新 (2026-06-12 23:55)\n\n- 加拿大 vs 波黑: 预测客场胜 1-2\n- 美国 vs 巴拉圭: 预测主场胜 2-1",
        "content": content_base64,
        "branch": BRANCH
    }
    if sha:
        commit_data["sha"] = sha
    
    # 推送文件
    print(f"\n正在推送到 GitHub...")
    response = requests.put(url, headers=headers, json=commit_data)
    
    if response.status_code in [200, 201]:
        result = response.json()
        commit_sha = result.get('commit', {}).get('sha', 'unknown')
        print(f"✅ 推送成功!")
        print(f"   Commit SHA: {commit_sha}")
        return commit_sha
    else:
        print(f"❌ 推送失败: {response.status_code}")
        print(f"   错误信息: {response.text}")
        return None

def trigger_pages_build(commit_sha):
    """触发GitHub Pages重新构建"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pages/builds"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    print(f"\n正在触发 GitHub Pages 重建...")
    response = requests.post(url, headers=headers)
    
    if response.status_code == 201:
        print(f"✅ GitHub Pages 重建已触发!")
        return True
    else:
        print(f"⚠️ 重建触发失败: {response.status_code}")
        return False

if __name__ == '__main__':
    if not GITHUB_TOKEN:
        print("❌ 未设置GITHUB_TOKEN环境变量")
        exit(1)
    
    commit_sha = push_to_github()
    if commit_sha:
        trigger_pages_build(commit_sha)
