#!/usr/bin/env python3
"""
QuarkPan CLI 主入口
"""

import logging
from typing import List, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

# 设置CLI模式下的日志级别为WARNING，减少日志输出
logging.getLogger("quark_client").setLevel(logging.WARNING)

from .commands.auth import auth_app
from .commands.basic_fileops import (browse_folder, create_folder,
                                     delete_files, file_info,
                                     get_download_link, goto_folder,
                                     rename_file, upload_file)
from .commands.download import download_app
from .commands.move_commands import move_files, move_to_folder
from .commands.search import search_app
from .commands.share_commands import create_share, list_my_shares, save_share
from .interactive import start_interactive
from .utils import (format_file_size, format_timestamp, get_client,
                    get_folder_name_by_id)

# 创建主应用
app = typer.Typer(
    name="quarkpan",
    help="🚀 夸克网盘命令行工具",
    rich_markup_mode="rich",
    no_args_is_help=True
)

# 添加子命令
app.add_typer(auth_app, name="auth", help="🔐 认证管理")

app.add_typer(search_app, name="search", help="🔍 文件搜索")
app.add_typer(download_app, name="download", help="📥 文件下载")


console = Console()


@app.command()
def interactive():
    """启动交互式模式"""
    start_interactive()


# 一级文件操作命令
@app.command()
def mkdir(
    folder_name: str = typer.Argument(..., help="文件夹名称"),
    parent_id: str = typer.Option("0", "--parent", "-p", help="父文件夹ID，默认为根目录")
):
    """创建文件夹"""
    create_folder(folder_name, parent_id)


@app.command()
def rm(
    paths: List[str] = typer.Argument(..., help="要删除的文件/文件夹路径或ID列表"),
    force: bool = typer.Option(False, "--force", "-f", help="强制删除，不询问确认"),
    use_id: bool = typer.Option(False, "--id", help="使用文件ID而不是路径")
):
    """删除文件或文件夹"""
    delete_files(paths, force, use_id)


@app.command()
def rename(
    path: str = typer.Argument(..., help="要重命名的文件/文件夹路径或ID"),
    new_name: str = typer.Argument(..., help="新名称"),
    use_id: bool = typer.Option(False, "--id", help="使用文件ID而不是路径")
):
    """重命名文件或文件夹"""
    rename_file(path, new_name, use_id)


@app.command()
def fileinfo(
    file_id: str = typer.Argument(..., help="文件/文件夹ID")
):
    """获取文件详细信息"""
    file_info(file_id)


@app.command()
def browse(
    folder_id: str = typer.Argument("0", help="文件夹ID，默认为根目录")
):
    """交互式文件夹浏览"""
    browse_folder(folder_id)


@app.command()
def goto(
    target: str = typer.Argument(..., help="目标文件夹（ID、名称或序号）"),
    current_folder: str = typer.Option("0", "--from", help="当前文件夹ID")
):
    """智能进入文件夹"""
    goto_folder(target, current_folder)


@app.command()
def upload(
    file_path: str = typer.Argument(..., help="要上传的文件路径"),
    parent_folder_id: str = typer.Option("0", "--parent", "-p", help="父文件夹ID，默认为根目录"),
    folder_path: Optional[str] = typer.Option(None, "--folder", "-f", help="目标文件夹路径，如 '/Documents/Photos'"),
    create_dirs: bool = typer.Option(False, "--create-dirs", "-c", help="自动创建不存在的文件夹")
):
    """上传文件到夸克网盘"""
    upload_file(file_path, parent_folder_id, folder_path, create_dirs)


# @app.command()
# def upload_dir(
#     folder_path: str = typer.Argument(..., help="要上传的文件夹路径"),
#     parent_folder_id: str = typer.Option("0", "--parent", "-p", help="父文件夹ID，默认为根目录"),
#     target_folder_path: Optional[str] = typer.Option(None, "--folder", "-f", help="目标文件夹路径，如 '/Documents/Photos'"),
#     create_dirs: bool = typer.Option(True, "--create-dirs/--no-create-dirs", help="自动创建不存在的文件夹（默认开启）"),
#     exclude_patterns: List[str] = typer.Option([], "--exclude", help="排除的文件模式，如 '*.tmp'"),
#     max_workers: int = typer.Option(3, "--workers", help="并发上传数量（1-10）")
# ):
#     """上传文件夹到夸克网盘"""
#     upload_folder(folder_path, parent_folder_id, target_folder_path, create_dirs, exclude_patterns, max_workers)


@app.command()
def share(
    file_paths: List[str] = typer.Argument(..., help="要分享的文件/文件夹路径或ID"),
    title: str = typer.Option("", "--title", "-t", help="分享标题"),
    expire_days: int = typer.Option(0, "--expire", "-e", help="过期天数，0表示永久"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="提取码"),
    use_id: bool = typer.Option(False, "--use-id", help="使用文件ID而不是路径")
):
    """创建分享链接"""
    create_share(file_paths, title, expire_days, password, use_id)


@app.command()
def shares(
    page: int = typer.Option(1, "--page", help="页码"),
    size: int = typer.Option(20, "--size", help="每页数量")
):
    """列出我的分享"""
    list_my_shares(page, size)


@app.command()
def save(
    share_url: str = typer.Argument(..., help="分享链接"),
    target_folder: str = typer.Option("/", "--folder", "-f", help="目标文件夹路径"),
    create_folder: bool = typer.Option(True, "--create-folder/--no-create-folder", help="自动创建目标文件夹")
):
    """转存分享文件"""
    save_share(share_url, target_folder, create_folder)


@app.command()
def move(
    source_paths: List[str] = typer.Argument(..., help="要移动的文件/文件夹路径或ID"),
    target_path: str = typer.Option(..., "--to", "-t", help="目标文件夹路径或ID"),
    use_id: bool = typer.Option(False, "--use-id", help="使用文件ID而不是路径")
):
    """移动文件到指定文件夹"""
    move_files(source_paths, target_path, use_id)


@app.command()
def mv(
    source_paths: List[str] = typer.Argument(..., help="要移动的文件/文件夹路径或ID"),
    target_path: str = typer.Option(..., "--to", "-t", help="目标文件夹路径或ID"),
    use_id: bool = typer.Option(False, "--use-id", help="使用文件ID而不是路径")
):
    """移动文件到指定文件夹（move的简写）"""
    move_files(source_paths, target_path, use_id)


@app.command()
def move_to(
    source_paths: List[str] = typer.Argument(..., help="要移动的文件/文件夹路径或ID"),
    folder_name: str = typer.Option(..., "--folder", "-f", help="目标文件夹名称"),
    parent_folder: str = typer.Option("/", "--parent", "-p", help="父文件夹路径"),
    create_folder: bool = typer.Option(True, "--create-folder/--no-create-folder", help="自动创建目标文件夹"),
    use_id: bool = typer.Option(False, "--use-id", help="使用文件ID而不是路径")
):
    """移动文件到指定名称的文件夹"""
    move_to_folder(source_paths, folder_name, parent_folder, create_folder, use_id)


@app.command()
def version():
    """显示版本信息"""
    rprint("[bold blue]QuarkPan CLI[/bold blue] [green]v1.0.0[/green]")
    rprint("夸克网盘命令行工具")


@app.command()
def status():
    """显示登录状态和存储信息"""
    try:
        with get_client() as client:
            # 检查登录状态
            if not client.is_logged_in():
                rprint("[red]❌ 未登录[/red]")
                rprint("请使用 [bold]quarkpan auth login[/bold] 登录")
                raise typer.Exit(1)

            rprint("[green]✅ 已登录[/green]")

            # 获取存储信息
            try:
                storage = client.get_storage_info()
                if storage and 'data' in storage:
                    data = storage['data']
                    total = data.get('total', 0)
                    used = data.get('used', 0)
                    free = total - used

                    # 创建存储信息表格
                    table = Table(title="💾 存储空间信息")
                    table.add_column("项目", style="cyan")
                    table.add_column("大小", style="green")
                    table.add_column("百分比", style="yellow")

                    usage_percent = (used / total * 100) if total > 0 else 0

                    table.add_row("总容量", format_file_size(total), "100%")
                    table.add_row("已使用", format_file_size(used), f"{usage_percent:.1f}%")
                    table.add_row("剩余", format_file_size(free), f"{100-usage_percent:.1f}%")

                    console.print(table)
                else:
                    rprint("[yellow]⚠️ 无法获取存储信息[/yellow]")
            except Exception as e:
                rprint(f"[yellow]⚠️ 获取存储信息失败: {e}[/yellow]")

            # 获取根目录文件数量
            try:
                files = client.list_files(size=1)
                if files and 'data' in files:
                    total_files = files['data'].get('total', 0)
                    rprint(f"\n📂 根目录文件数量: [bold]{total_files}[/bold]")
                else:
                    rprint("\n[yellow]⚠️ 无法获取文件信息[/yellow]")
            except Exception as e:
                rprint(f"\n[yellow]⚠️ 获取文件信息失败: {e}[/yellow]")

    except Exception as e:
        rprint(f"[red]❌ 错误: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def ls(
    folder_id: str = typer.Argument("0", help="文件夹ID，默认为根目录"),
    page: int = typer.Option(1, "--page", "-p", help="页码"),
    size: int = typer.Option(20, "--size", "-s", help="每页数量"),
    sort_field: str = typer.Option("file_name", "--sort", help="排序字段"),
    sort_order: str = typer.Option("asc", "--order", help="排序方向 (asc/desc)"),
    show_details: bool = typer.Option(False, "--details", "-d", help="显示详细信息"),
    folders_only: bool = typer.Option(False, "--folders-only", help="只显示文件夹"),
    files_only: bool = typer.Option(False, "--files-only", help="只显示文件")
):
    """列出文件和文件夹"""
    try:
        with get_client() as client:
            if not client.is_logged_in():
                rprint("[red]❌ 未登录，请先使用 quarkpan auth login 登录[/red]")
                raise typer.Exit(1)

            # 根据过滤选项选择API调用
            if folders_only or files_only:
                files = client.list_files_with_details(
                    folder_id=folder_id,
                    page=page,
                    size=size,
                    sort_field=sort_field,
                    sort_order=sort_order,
                    include_folders=not files_only,
                    include_files=not folders_only
                )
            else:
                files = client.list_files(
                    folder_id=folder_id,
                    page=page,
                    size=size,
                    sort_field=sort_field,
                    sort_order=sort_order
                )

            if not files or 'data' not in files:
                rprint("[red]❌ 无法获取文件列表[/red]")
                raise typer.Exit(1)

            file_list = files['data'].get('list', [])
            total = files['data'].get('total', 0)

            # 显示标题
            folder_name = get_folder_name_by_id(client, folder_id)
            rprint(f"\n📂 [bold]{folder_name}[/bold] (第{page}页，共{total}个项目)")

            if not file_list:
                rprint("[yellow]📂 文件夹为空[/yellow]")
                return

            if show_details:
                # 详细表格视图
                table = Table()
                table.add_column("序号", style="dim")
                table.add_column("类型", style="cyan")
                table.add_column("名称", style="white")
                table.add_column("大小", style="green")
                table.add_column("修改时间", style="yellow")

                for i, file_info in enumerate(file_list, (page - 1) * size + 1):
                    name = file_info.get('file_name', '未知')
                    size_bytes = file_info.get('size', 0)
                    file_type = file_info.get('file_type', 0)
                    updated_at = file_info.get('updated_at', '')

                    type_icon = "📁" if file_type == 0 else "📄"
                    size_str = "-" if file_type == 0 else format_file_size(size_bytes)
                    time_str = format_timestamp(updated_at) if updated_at else "-"

                    table.add_row(str(i), type_icon, name, size_str, time_str)

                console.print(table)
            else:
                # 简洁列表视图
                for i, file_info in enumerate(file_list, (page - 1) * size + 1):
                    name = file_info.get('file_name', '未知')
                    file_type = file_info.get('file_type', 0)
                    type_icon = "📁" if file_type == 0 else "📄"

                    rprint(f"  {i:2d}. {type_icon} {name}")

            # 显示分页信息
            if total > size:
                total_pages = (total + size - 1) // size
                rprint(f"\n[dim]第 {page}/{total_pages} 页，共 {total} 个项目[/dim]")
                if page < total_pages:
                    rprint(f"[dim]使用 --page {page + 1} 查看下一页[/dim]")

            # 显示交互提示
            if not show_details:
                folders = [f for f in file_list if f.get('file_type', 0) == 0]
                if folders:
                    rprint(f"\n[dim]💡 提示: 使用 [cyan]quarkpan files browse[/cyan] 进行交互式浏览[/dim]")
                    rprint(f"[dim]或使用 [cyan]quarkpan ls <文件夹ID>[/cyan] 进入指定文件夹[/dim]")

    except Exception as e:
        rprint(f"[red]❌ 错误: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def cd(
    folder_id: str = typer.Argument(..., help="要进入的文件夹ID"),
    show_details: bool = typer.Option(False, "--details", "-d", help="显示详细信息")
):
    """进入指定文件夹 (快捷命令)"""
    try:
        with get_client() as client:
            if not client.is_logged_in():
                rprint("[red]❌ 未登录，请先使用 quarkpan auth login 登录[/red]")
                raise typer.Exit(1)

            # 获取文件夹名称
            folder_name = get_folder_name_by_id(client, folder_id)

            # 列出文件夹内容
            files = client.list_files(folder_id=folder_id, size=20)

            if not files or 'data' not in files:
                rprint("[red]❌ 无法获取文件列表或文件夹不存在[/red]")
                raise typer.Exit(1)

            file_list = files['data'].get('list', [])
            total = files['data'].get('total', 0)

            rprint(f"\n📂 [bold]{folder_name}[/bold] ({total}个项目)")

            if not file_list:
                rprint("[yellow]📂 文件夹为空[/yellow]")
                return

            if show_details:
                # 详细表格视图
                from rich.table import Table
                table = Table()
                table.add_column("序号", style="dim")
                table.add_column("类型", style="cyan")
                table.add_column("名称", style="white")
                table.add_column("大小", style="green")
                table.add_column("修改时间", style="yellow")
                table.add_column("ID", style="dim")

                for i, file_info in enumerate(file_list, 1):
                    name = file_info.get('file_name', '未知')
                    size_bytes = file_info.get('size', 0)
                    file_type = file_info.get('file_type', 0)
                    updated_at = file_info.get('updated_at', '')
                    fid = file_info.get('fid', '')

                    from .utils import get_file_type_icon
                    is_folder = file_type == 0
                    type_icon = get_file_type_icon(name, is_folder)
                    size_str = "-" if is_folder else format_file_size(size_bytes)
                    time_str = format_timestamp(updated_at) if updated_at else "-"
                    short_id = fid[:8] + "..." if len(fid) > 8 else fid

                    table.add_row(str(i), type_icon, name, size_str, time_str, short_id)

                console.print(table)
            else:
                # 简洁列表视图
                for i, file_info in enumerate(file_list, 1):
                    name = file_info.get('file_name', '未知')
                    file_type = file_info.get('file_type', 0)
                    from .utils import get_file_type_icon
                    type_icon = get_file_type_icon(name, file_type == 0)

                    rprint(f"  {i:2d}. {type_icon} {name}")

            # 显示交互提示
            folders = [f for f in file_list if f.get('file_type', 0) == 0]
            if folders:
                rprint(f"\n[dim]💡 提示: 使用 [cyan]quarkpan files browse[/cyan] 进行交互式浏览[/dim]")

    except Exception as e:
        rprint(f"[red]❌ 错误: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def info():
    """显示帮助信息"""
    rprint("""
[bold blue]QuarkPan CLI - 夸克网盘命令行工具[/bold blue]

[bold]主要命令:[/bold]
  [cyan]quarkpan interactive[/cyan]    - 启动交互式模式 🌟
  [cyan]quarkpan auth login[/cyan]     - 登录夸克网盘
  [cyan]quarkpan auth logout[/cyan]    - 登出
  [cyan]quarkpan status[/cyan]         - 显示状态信息
  [cyan]quarkpan ls[/cyan]             - 列出文件和文件夹

[bold]高级功能:[/bold]
  [cyan]quarkpan browse[/cyan]         - 交互式浏览文件夹
  [cyan]quarkpan goto <target>[/cyan]  - 智能进入文件夹
  [cyan]quarkpan fileinfo <id>[/cyan]  - 获取文件详细信息

[bold]搜索功能:[/bold]
  [cyan]quarkpan search "关键词"[/cyan]  - 基础搜索
  [cyan]quarkpan search --ext pdf[/cyan] - 按扩展名搜索
  [cyan]quarkpan search --details[/cyan]  - 详细搜索结果
  [cyan]quarkpan search --min-size 1MB[/cyan] - 按大小搜索

[bold]下载功能:[/bold]
  [cyan]quarkpan download file <file_id>[/cyan] - 下载单个文件
  [cyan]quarkpan download files <file_id>...[/cyan] - 批量下载文件
  [cyan]quarkpan download folder <folder_id>[/cyan] - 下载文件夹
  [cyan]quarkpan download info[/cyan] - 下载说明

[bold]文件操作:[/bold]
  [cyan]quarkpan mkdir <name>[/cyan] - 创建文件夹
  [cyan]quarkpan rm <path>...[/cyan] - 删除文件/文件夹
  [cyan]quarkpan rename <path> <name>[/cyan] - 重命名文件/文件夹

[bold]文件上传:[/bold]
  [cyan]quarkpan upload <file_path>[/cyan] - 上传文件

[bold]示例:[/bold]
  [dim]# 登录[/dim]
  quarkpan auth login

  [dim]# 查看根目录[/dim]
  quarkpan ls

  [dim]# 详细列表[/dim]
  quarkpan ls --details

  [dim]# 交互式浏览[/dim]
  quarkpan browse

  [dim]# 智能进入文件夹[/dim]
  quarkpan goto "分享"

  [dim]# 搜索文件[/dim]
  quarkpan search "文档"

  [dim]# 高级搜索[/dim]
  quarkpan search --ext pdf --min-size 1MB "课程"

  [dim]# 下载文件[/dim]
  quarkpan download file 0d51b7344d894d20a671a5c567383749

  [dim]# 文件操作[/dim]
  quarkpan mkdir "我的文档"
  quarkpan rm "文件名.txt"
  quarkpan rename "旧名称" "新名称"

  [dim]# 上传文件[/dim]
  quarkpan upload "document.pdf"

  [dim]# 获取文件信息[/dim]
  quarkpan fileinfo 0d51b7344d894d20a671a5c567383749

更多帮助请使用: [cyan]quarkpan COMMAND --help[/cyan]
""")


if __name__ == "__main__":
    app()
