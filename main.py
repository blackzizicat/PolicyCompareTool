import functions
import os
import zipfile
import shutil
import glob
import subprocess
from bs4 import BeautifulSoup


if __name__ == "__main__":

    download_dir = "/mnt/download"

    # Webからファイルを取得
    try:
        # windows
        win_latest_policy_link = functions.clicker(
            "https://learn.microsoft.com/en-us/troubleshoot/windows-client/group-policy/create-and-manage-central-store",
            '//*[@id="main"]/div[2]/div[1]/div[6]/ul[1]/li[2]/a'
        )
        win_download_link = functions.clicker(win_latest_policy_link,'//*[@id="rootContainer_DLCDetails"]/section[3]/div/div/div/div/div/a')
        functions.clicker(win_download_link)
        
        # edge
        edge_download_link = functions.clicker(
            "https://www.microsoft.com/ja-jp/edge/business/download",
            '//*[@id="main"]/div/div[1]/div[1]/section[1]/div/div/div/div[3]/div[1]/div[2]/button[2]'
        )
        functions.clicker(edge_download_link)

        # chrome
        functions.clicker("https://dl.google.com/dl/edgedl/chrome/policy/policy_templates.zip")
        functions.clicker("http://dl.google.com/update2/enterprise/googleupdateadmx.zip")

        # # office
        # office_download_link = functions.clicker(
        #     "https://www.microsoft.com/en-us/download/details.aspx?id=49030",
        #     '//*[@id="rootContainer_DLCDetails"]/section[3]/div/div/div/div/div/button'
        # )
        # functions.clicker(office_download_link)

    finally:
        functions.driver.quit()


    # ファイルを比較可能な状態に整える
    # 必要なディレクトリを作成
    os.makedirs(f"{download_dir}/new_policy/", exist_ok=True)

    # .cab ファイルを .zip に変換する
    subprocess.run(["cabextract", "-d", download_dir, f"{download_dir}/MicrosoftEdgePolicyTemplates.cab"])

    # downloadディレクトリ内の .zip を解凍
    # 解凍先のベースディレクトリ
    base_extract_dir = f"{download_dir}/new_policy/"
    # `.zip` ファイルを検索
    zip_files = glob.glob(os.path.join(download_dir, "*.zip"))

    # 各 `.zip` ファイルを解凍
    for zip_file in zip_files:
        # ファイル名からフォルダ名を生成（拡張子を除去）
        folder_name = os.path.splitext(os.path.basename(zip_file))[0]
        extract_path = os.path.join(base_extract_dir, folder_name)

        # 解凍処理
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_path)

    # downloadディレクトリ内の .msi .exe を展開
    # `.msi` または `.exe` の拡張子を持つファイルを検索
    files = glob.glob(os.path.join(download_dir, "*.msi")) + glob.glob(os.path.join(download_dir, "*.exe"))

    # 検出したファイルを順番に展開
    for file in files:
        subprocess.run(["7z", "x", file, f"-o{base_extract_dir}"], check=True)

    # # 解凍前のファイルを削除
    # for file_extension in ["*.zip", "*.cab", "*.msi", "*.exe"]:
    #     for file in glob.glob(f"{download_dir}/{file_extension}"):
    #         os.remove(file)

    # OneDrive.admlを移動
    one_drive_admx = f"{download_dir}/adm/OneDrive.admx"
    one_drive_adml = f"{download_dir}/adm/OneDrive.adml"
    if os.path.exists(one_drive_admx):
        shutil.copy(one_drive_admx, f"{download_dir}/new_policy/")
        shutil.copy(one_drive_adml, f"{download_dir}/new_policy/")

    # 既存ポリシーテンプレートを複製
    shutil.copytree(
        f"{download_dir}/PolicyDefinitions/",
        f"{download_dir}/new_PolicyDefinitions/",
        dirs_exist_ok=True
    )


source_folder = f"{download_dir}/new_policy"
destination_folder = f"{download_dir}/new_PolicyDefinitions"

def find_files_by_name(root_dir, filename, case_insensitive=True):
    """root_dir配下で、同名のファイルパスをすべて返す"""
    matches = []
    for r, d, files in os.walk(root_dir):
        for f in files:
            if case_insensitive:
                if f.lower() == filename.lower():
                    matches.append(os.path.join(r, f))
            else:
                if f == filename:
                    matches.append(os.path.join(r, f))
    return matches


for root, dirs, files in os.walk(source_folder):
    # "xx-XX"や"xx-XXX"のロケール風サブフォルダは ja-JP/ja-jp 以外スキップ
    parts = root.split(os.sep)
    if any(p for p in parts if p.lower() != "ja-jp" and len(p) >= 5 and '-' in p):
        continue

    for file in files:
        source_file = os.path.join(root, file)

        # すべてのファイルについてコピー先全体を検索（柔軟運用）
        search_root = destination_folder

        # 同名ファイルをコピー先で検索（フォルダ階層は無視）
        candidates = find_files_by_name(search_root, file, case_insensitive=True)

        if not candidates:
            # 見つからなければ何もしない
            # print(f"スキップ（同名ファイルなし）: {file}")
            continue

        # 見つかった同名ファイルすべてを上書き
        for dest_path in candidates:
            shutil.copy2(source_file, dest_path)


    # admlファイルを比較する
    # フォルダAとフォルダBのパスを指定
    folder_a = f"{download_dir}/PolicyDefinitions/ja-JP"
    folder_b = f"{download_dir}/new_PolicyDefinitions/ja-JP"
    output_folder = "/mnt/DiffOutput"  # 差分出力用のフォルダ

    # 差分出力フォルダを作成（存在しない場合）
    os.makedirs(output_folder, exist_ok=True)

    # フォルダA内のすべての`.adml`ファイルを取得
    for root_a, _, files_a in os.walk(folder_a):
        for file_name in files_a:
            if not file_name.endswith('.adml'):
                continue

            file_a_path = os.path.join(root_a, file_name)

            # フォルダBの `ja-JP` 内に同じファイルがあるか確認
            corresponding_b_path = os.path.join(folder_b, os.path.relpath(file_a_path, folder_a))

            # フォルダBに対応するファイルが存在する場合のみ比較
            if os.path.exists(corresponding_b_path):
                functions.compare_text_files(file_a_path, corresponding_b_path, 'utf-16', file_name, output_folder)
                functions.compare_text_files(file_a_path, corresponding_b_path, 'utf-8', file_name, output_folder)


    # 差分ファイルに使用中のポリシーが含まれているか確認する
    output_file = "/mnt/output_results.txt"  # 出力ファイルのパス

    # 出力ファイルを初期化
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("検索結果:\n\n")

    # "PolicyReport" を含むフォルダを検索
    for root, dirs, files in os.walk(download_dir):
        for dir_name in dirs:
            if "PolicyReport" in dir_name:
                policy_report_folder = os.path.join(root, dir_name)
    
    # フォルダ内のすべてのファイルを処理
    for root, _, files in os.walk(policy_report_folder):
        for file in files:
            file_path = os.path.join(root, file)
            
            # HTMLファイルを読み込む
            with open(file_path, 'r', encoding='utf-16') as html_file:
                html_content = html_file.read()

            # BeautifulSoupオブジェクトの作成
            soup = BeautifulSoup(html_content, 'html.parser')

            # すべての span タグを取得し、gpmc_settingname 属性の値を抽出
            spans = soup.find_all('span', attrs={'gpmc_settingname': True})
            for span in spans:
                gpmc_settingname_value = span['gpmc_settingname']
                
                # DiffOutputフォルダ内で検索 (元のHTMLファイル名を渡す)
                functions.search_in_diff_output_folder(gpmc_settingname_value, output_folder, file_path, output_file)

    print(f"検索結果を {output_file} に保存しました。")

