#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
【改訂完全版】Playwright版 fam8キャンペーンCSV取得処理（一般→アダルト）
自動実行用スクリプト: get_campaign_csv_auto_2mode.py
機能: fam8の管理画面にログインし、一般とアダルトのCSVを連続自動取得
"""
import os
import sys
import time
import asyncio
import logging
import shutil
from datetime import datetime
from logging.handlers import RotatingFileHandler
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# 設定情報
CONFIG = {
    # ログイン情報
    "LOGIN": {
        "url": "https://admin.fam-8.net/report/index.php",
        "email": "admin",
        "password": "fhC7UPJiforgKTJ8"
    },
    
    # パス設定
    "PATHS": {
        "downloads": os.path.join(os.path.dirname(os.path.abspath(__file__)), "tmp_downloads"),
        "destination": r"\\rin\rep\営業本部\プロジェクト\fam\ADN\各ADN進捗表\fam8進捗\キャンペーンレポートCSV",
        "log_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
    },
    
    # タイムアウト（ミリ秒）
    "TIMEOUT": {
        "page": 600000,  # 10分
        "navigation": 90000,
        "download": 120000,
        "search_result": 300000  # 検索結果の表示待ち時間: 5分
    },
    
    # 待機時間（秒）
    "WAIT": {
        "between_steps": 30,
        "after_click": 2,
        "after_search": 120  # 検索ボタン押下後の固定待機時間: 2分
    },
    
    # ブラウザ設定
    "BROWSER": {
        "headless": False,
        "incognito": True
    },
    
    # XPath・CSSセレクタ設定
    "XPATH": {
        "login": {
            "email": "//*[@id='topmenu']/tbody/tr[2]/td/div[1]/form/div/table/tbody/tr[1]/td/input",
            "password": "//*[@id='topmenu']/tbody/tr[2]/td/div[1]/form/div/table/tbody/tr[2]/td/input",
            "button": "//*[@id='topmenu']/tbody/tr[2]/td/div[1]/form/div/table/tbody/tr[3]/td/input[2]"
        },
        "menu": {
            "campaign": "//*[@id='sidemenu']/div[1]/a[8]/div"
        },
        "checkboxes": {
            "general": "//*[@id='main_area']/form/div[1]/table/tbody/tr[1]/td[1]/input[2]",
            "adult": "//*[@id='main_area']/form/div[1]/table/tbody/tr[2]/td[1]/input[2]"
        },
        "csv_button": "//*[@id='topmenu']/table/tbody/tr/td[4]/table/tbody/tr[2]/td[2]/input[1]"
    },
    "CSS": {
        "search": {
            "agency_dropdown": "#main_area > form > div.where > select:nth-child(34)",
            "condition_dropdown": "#main_area > form > div.where > select:nth-child(35)",
            "keyword_input": "#main_area > form > div.where > input:nth-child(36)",
            "search_button": "#main_area > form > div.where > input[type='button'][value='検索']"
        },
        "csv_button": "input.btn_exp.csv"
    }
}

# ロガー設定
def setup_logger():
    """ロギング設定を初期化し、ファイルとコンソール出力のロガーを返す"""
    today = datetime.now().strftime('%Y%m%d分')
    log_file = os.path.join(CONFIG["PATHS"]["log_dir"], f"{today}.log")
    
    os.makedirs(CONFIG["PATHS"]["log_dir"], exist_ok=True)
    
    logger = logging.getLogger('fam8_campaign')
    logger.setLevel(logging.INFO)
    
    if logger.handlers:
        logger.handlers.clear()
    
    log_format = logging.Formatter('[%(levelname)s] %(asctime)s → %(message)s', '%Y-%m-%d %H:%M:%S')
    
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    return logger

async def main():
    """メイン処理: ブラウザ起動からCSV取得までの一連の流れを制御"""
    logger = setup_logger()
    logger.info("fam8キャンペーンCSV取得処理を開始します")
    
    os.makedirs(CONFIG["PATHS"]["downloads"], exist_ok=True)
    
    # 年月日形式のフォルダを作成
    today_folder_name = datetime.now().strftime('%Y%m%d')
    today_folder_path = os.path.join(CONFIG["PATHS"]["destination"], today_folder_name)
    
    # フォルダが存在しない場合は作成
    if not os.path.exists(today_folder_path):
        os.makedirs(today_folder_path, exist_ok=True)
        logger.info(f"日付フォルダを作成しました: {today_folder_path}")
    else:
        logger.info(f"日付フォルダは既に存在します: {today_folder_path}")
    
    async with async_playwright() as playwright:
        browser_launch_options = {"headless": CONFIG["BROWSER"]["headless"]}
        
        logger.info("ブラウザを起動しています...")
        browser = await playwright.chromium.launch(**browser_launch_options)
        
        context_options = {
            "accept_downloads": True,
            "viewport": {"width": 1280, "height": 800}
        }
        
        if CONFIG["BROWSER"]["incognito"]:
            logger.info("シークレットモードでコンテキストを作成します")
        
        context = await browser.new_context(**context_options)
        page = await context.new_page()
        
        page.set_default_timeout(CONFIG["TIMEOUT"]["page"])
        page.set_default_navigation_timeout(CONFIG["TIMEOUT"]["navigation"])
        
        try:
            await login(page, logger)
            
            # 一般モードのCSV取得
            await process_csv(page, logger, "general", today_folder_path)
            
            logger.info(f"{CONFIG['WAIT']['between_steps']}秒間待機します...")
            await asyncio.sleep(CONFIG["WAIT"]["between_steps"])
            
            # アダルトモードのCSV取得
            await process_csv(page, logger, "adult", today_folder_path)
            
            logger.info("すべての処理が完了しました")
            
        except Exception as e:
            logger.error(f"エラーが発生しました: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            await browser.close()
            logger.info("ブラウザを終了しました")

async def login(page, logger):
    """ログイン処理を実行"""
    logger.info("ログイン処理を開始します")
    
    await page.goto(CONFIG["LOGIN"]["url"])
    logger.info(f"ログインページにアクセスしました: {CONFIG['LOGIN']['url']}")
    
    await page.fill(CONFIG["XPATH"]["login"]["email"], CONFIG["LOGIN"]["email"])
    await page.fill(CONFIG["XPATH"]["login"]["password"], CONFIG["LOGIN"]["password"])
    
    await page.click(CONFIG["XPATH"]["login"]["button"])
    await page.wait_for_load_state("networkidle")
    
    logger.info("ログインに成功しました")
    
    await page.click(CONFIG["XPATH"]["menu"]["campaign"])
    await page.wait_for_load_state("networkidle")
    
    logger.info("キャンペーン画面に遷移しました")

async def process_csv(page, logger, mode, today_folder_path):
    """CSV取得処理（一般/アダルト共通）"""
    mode_jp = "一般" if mode == "general" else "アダルト"
    mode_en = "general" if mode == "general" else "adult"
    start_time = time.time()
    logger.info(f"{mode_jp}モードでのCSV取得処理を開始します")
    
    general_checkbox = CONFIG["XPATH"]["checkboxes"]["general"]
    adult_checkbox = CONFIG["XPATH"]["checkboxes"]["adult"]
    
    if mode == "general":
        # 「一般」モードの場合：アダルトチェックを外す
        adult_checked = await page.is_checked(adult_checkbox)
        if adult_checked:
            await page.click(adult_checkbox)
            logger.info("「アダルト」チェックボックスを解除しました")
            await asyncio.sleep(CONFIG["WAIT"]["after_click"])
    else:
        # 「アダルト」モードの場合：一般チェックを外し、アダルトチェックを入れる
        general_checked = await page.is_checked(general_checkbox)
        if general_checked:
            await page.click(general_checkbox)
            logger.info("「一般」チェックボックスを解除しました")
            await asyncio.sleep(CONFIG["WAIT"]["after_click"])
        
        adult_checked = await page.is_checked(adult_checkbox)
        if not adult_checked:
            await page.click(adult_checkbox)
            logger.info("「アダルト」チェックボックスを選択しました")
            await asyncio.sleep(CONFIG["WAIT"]["after_click"])
    
    # 代理店名プルダウン選択 - JavaScriptで直接実行
    await page.evaluate("""
        (() => {
            // 代理店名ドロップダウンの取得
            const agencyDropdown = document.querySelector("#main_area > form > div.where > select:nth-child(34)");
            if (!agencyDropdown) return;
            
            // オプション一覧を取得
            const options = Array.from(agencyDropdown.options);
            
            // 7番目を選択
            if (options.length >= 7) {
                agencyDropdown.selectedIndex = 6; // 0ベースなので7番目は6
                agencyDropdown.dispatchEvent(new Event('change', { bubbles: true }));
            }
        })();
    """)
    logger.info("代理店名を選択しました")
    await asyncio.sleep(CONFIG["WAIT"]["after_click"])
    
    # 検索条件プルダウン選択 - JavaScriptで直接実行
    await page.evaluate("""
        (() => {
            // 検索条件ドロップダウンの取得
            const conditionDropdown = document.querySelector("#main_area > form > div.where > select:nth-child(35)");
            if (!conditionDropdown) return;
            
            // オプション一覧を取得
            const options = Array.from(conditionDropdown.options);
            
            // 5番目を選択
            if (options.length >= 5) {
                conditionDropdown.selectedIndex = 4; // 0ベースなので5番目は4
                conditionDropdown.dispatchEvent(new Event('change', { bubbles: true }));
            }
        })();
    """)
    logger.info("検索条件を選択しました")
    await asyncio.sleep(CONFIG["WAIT"]["after_click"])
    
    # キーワード入力
    await page.fill(CONFIG["CSS"]["search"]["keyword_input"], "9999")
    logger.info("検索語（9999）を入力しました")
    await asyncio.sleep(CONFIG["WAIT"]["after_click"])
    
    # Enterキーを2回押す
    logger.info("Enterキーを押します（1回目）...")
    await page.keyboard.press("Enter")
    logger.info("Enterキーを押しました（1回目）")
    
    # 1秒待機
    await asyncio.sleep(1)
    
    logger.info("Enterキーを押します（2回目）...")
    await page.keyboard.press("Enter")
    logger.info("Enterキーを押しました（2回目）")
    
    # 検索結果表示を待機
    logger.info(f"検索結果待機中... ({CONFIG['WAIT']['after_search']}秒)")
    await asyncio.sleep(CONFIG["WAIT"]["after_search"])
    
    search_time = int(time.time() - start_time)
    logger.info(f"{mode_jp}CSV検索処理完了（処理時間：{search_time}秒）")
    
    # CSVダウンロードボタンクリック
    logger.info("CSVダウンロードボタンをクリックします...")
    
    try:
        # JavaScriptでsub_export関数を直接呼び出す
        async with page.expect_download(timeout=CONFIG["TIMEOUT"]["download"]) as download_info:
            await page.evaluate("sub_export('csv')")
            logger.info("JavaScriptでCSV出力関数を実行しました")
        
        download = await download_info.value
        logger.info(f"ダウンロードが開始されました: {download.suggested_filename}")
        
        today = datetime.now().strftime('%Y-%m-%d')
        original_filename = download.suggested_filename
        download_path = os.path.join(CONFIG["PATHS"]["downloads"], original_filename)
        
        await download.save_as(download_path)
        logger.info(f"CSVファイルをダウンロードしました: {download_path}")
        
        # ファイルの存在確認
        if not os.path.exists(download_path):
            raise FileNotFoundError(f"ダウンロードしたファイルが見つかりません: {download_path}")
        
        file_size = os.path.getsize(download_path)
        logger.info(f"ダウンロードしたファイルのサイズ: {file_size} バイト")
        
        # 英語表記を使用してファイル名を作成
        renamed_filename = f"affiliate_article_{today}_{mode_en}.csv"
        
        # 日付フォルダ内にファイルを保存
        renamed_path = os.path.join(today_folder_path, renamed_filename)
        
        # ファイルが既に存在する場合は上書き
        if os.path.exists(renamed_path):
            logger.info(f"既存のファイルを上書きします: {renamed_path}")
            os.remove(renamed_path)
        
        shutil.copy2(download_path, renamed_path)
        logger.info(f"{mode_jp}CSV保存：{renamed_path}")
        
        return True
    except Exception as e:
        logger.error(f"CSVダウンロードエラー: {str(e)}")
        raise Exception("CSVダウンロードに失敗しました")

if __name__ == "__main__":
    asyncio.run(main())