# Telloドローンプロジェクト

DJI Tello ドローンをPythonでプログラミングするためのプロジェクトです。

## 環境構築

このプロジェクトは `uv` を使用して環境を管理しています。

### 必要なもの
- Python 3.12以上
- uv（Pythonパッケージマネージャー）
- DJI Tello ドローン

### セットアップ手順

1. uvがインストールされていない場合は、まずuvをインストールしてください：
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. リポジトリをクローン：
```bash
git clone <your-repository-url>
cd tello
```

3. 仮想環境を作成：
```bash
uv venv
```

4. 仮想環境をアクティベート：
```powershell
# Windows (PowerShell)
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

5. 必要なパッケージをインストール：
```bash
uv pip install djitellopy
```

## プログラムファイル

- `test.py` - 基本的な離陸・着陸テストプログラム
- `circle.py` - カメラを中心に向けながら円を描くプログラム（録画機能付き）

## 使い方

### 基本テスト
```bash
python test.py
```

### 円飛行（録画付き）
```bash
python circle.py
```

## 注意事項

- バッテリー残量が20%未満の場合、プログラムは自動的に停止します
- 録画ファイルは `.avi` 形式で保存されます
- 屋内で十分なスペースを確保してから実行してください
- Telloのファームウェアが最新であることを確認してください

## ライセンス

このプロジェクトは個人の学習・研究目的で作成されています。

## インストールされるパッケージ

- `djitellopy==2.5.0` - Tello SDK のPythonラッパー
- `opencv-python==4.11.0.86` - 画像処理・録画用
- `numpy==2.3.3` - 数値計算用
- `av==15.1.0` - 動画処理用
- `pillow==11.3.0` - 画像処理用
