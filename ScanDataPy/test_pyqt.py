try:
    import PyQt6
    print(f"PyQt6は {PyQt6.__file__} にインストールされています")
    print(f"Qt6のライブラリディレクトリは {PyQt6.__path__} です")
except ImportError as e:
    print(f"PyQt6をインポートできませんでした: {e}")