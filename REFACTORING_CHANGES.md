# イベント駆動型アーキテクチャへのリファクタリング変更履歴

## 概要
QtDataWindowとDataController間の循環参照を解消し、イベント駆動型アーキテクチャに移行しました。

## 作成したファイル

### 1. **ScanDataPy/common_event.py** (新規作成)
イベントシステムの基盤となるファイル。ViewとController間の通信を管理。

#### 主要クラス：
- `ViewEvent`: ビューイベントの基底クラス
- `ViewEventBus`: View→Controller通信用のイベントバス
  - `file_open_requested`: ファイルオープン要求
  - `roi_size_change_requested`: ROIサイズ変更要求
  - `roi_clicked`: ROIクリックイベント
  - `bl_roi_mode_changed`: ベースラインROIモード変更
  - `bl_use_roi1_changed`: ベースラインROI選択変更
  - `modifier_value_change_requested`: モディファイア値変更要求
  - `scale_mode_changed`: スケールモード変更
  - `bl_comp_toggled`: ベースライン補正切り替え
  - `dif_image_toggled`: 差分画像切り替え
  - `invert_toggled`: 反転切り替え
  - `fluo_channel_changed`: 蛍光チャンネル変更
  - `elec_channel_changed`: 電気チャンネル変更
  - `time_window_change_requested`: タイムウィンドウ変更要求
  - `view_update_requested`: ビュー更新要求
  - `marker_update_requested`: マーカー更新要求
  - `axes_sync_requested`: 軸同期要求

- `ControllerEventBus`: Controller→View通信用のイベントバス
  - `data_loaded`: データロード完了
  - `axes_data_updated`: 軸データ更新
  - `roi_marker_updated`: ROIマーカー更新
  - `modifier_state_changed`: モディファイア状態変更
  - `float_window_requested`: フロートウィンドウ要求
  - `status_message`: ステータスメッセージ
  - `error_occurred`: エラー発生

### 2. **ScanDataPy/controller/controller_data_refactored.py** (リファクタリング版)
DataControllerの改善版。Viewへの直接参照を削除し、イベント駆動型に変更。

#### 主な変更点：
- Viewへの参照を削除（`self._data_window`を削除）
- `ViewEventBus`と`ControllerEventBus`を追加
- `initialize_axes()`メソッドを追加（ウィンドウ作成後に軸を初期化）
- すべてのView操作をイベントハンドラー経由に変更：
  - `_handle_file_open()`
  - `_handle_roi_size_change()`
  - `_handle_roi_click()`
  - `_handle_bl_roi_mode_change()`
  - `_handle_bl_use_roi1_change()`
  - `_handle_modifier_value_change()`
  - `_handle_scale_mode_change()`
  - `_handle_bl_comp_toggle()`
  - `_handle_dif_image_toggle()`
  - `_handle_invert_toggle()`
  - `_handle_fluo_channel_change()`
  - `_handle_elec_channel_change()`
  - `_handle_time_window_change()`
  - `_handle_view_update_request()`
  - `_handle_axes_sync()`
- AxesControllerの作成をDataController内で実行

### 3. **ScanDataPy/view/view_data_refactored.py** (リファクタリング版)
QtDataWindowの改善版。DataControllerへの直接呼び出しを削除し、イベント発行に変更。

#### 主な変更点：
- `self._data_controller`への直接参照を削除
- `view_event_bus`と`controller_event_bus`を受け取るように変更
- すべてのボタン・チェックボックスのコールバックをイベント発行に変更
- ビジネスロジックをControllerに移動：
  - `scale()`メソッドの処理をイベント発行に変更
  - `bl_comp()`メソッドの処理をイベント発行に変更
  - `switch_ch()`メソッドの処理をイベント発行に変更
  - その他すべての処理メソッドをイベント発行に変更
- Controllerからのイベントを受信するハンドラーを追加：
  - `_on_data_loaded()`
  - `_on_axes_updated()`
  - `_on_roi_marker_updated()`
  - `_on_float_window_requested()`
  - `_on_status_message()`
  - `_on_error()`
- `get_axes_config()`メソッドを追加（軸設定をControllerに渡すため）

### 4. **ScanDataPy/controller/controller_main_refactored.py** (リファクタリング版)
MainControllerの改善版。ViewとControllerを独立して作成し、循環依存を解消。

#### 主な変更点：
- DataControllerの作成時にViewを渡さないように変更
- `_create_data_window()`メソッドで以下の手順を実装：
  1. DataControllerを作成（Viewへの参照なし）
  2. DataWindowを作成（イベントバスを渡す）
  3. 軸設定を取得してDataControllerで初期化
  4. ウィンドウを表示
- 複数のDataControllerを管理できるように`data_controllers`リストを追加
- ウィンドウクローズ時のクリーンアップ処理を追加

### 5. **migrate_to_event_driven.py** (新規作成)
既存のコードベースを新しいアーキテクチャに移行するためのスクリプト。

#### 機能：
- 既存ファイルのバックアップ作成（タイムスタンプ付き）
- リファクタリング版ファイルを本番ファイルに置き換え
- インポート文の更新
- アーキテクチャの概要表示

## アーキテクチャの変更点

### 変更前の問題点：
1. QtDataWindowがDataControllerを直接参照（`self._data_controller`）
2. DataControllerがQtDataWindowを作成（循環依存）
3. ViewがControllerのメソッドを直接呼び出し
4. AxesControllerの作成がView内で実行
5. ViewとControllerが密結合

### 変更後の改善点：
1. **単方向の依存関係**
   - Controller → View（イベントバス経由）
   - Viewは直接Controllerを知らない

2. **イベント駆動型通信**
   - すべてのView操作はイベントとして発行
   - ControllerはイベントハンドラーでView要求を処理
   - ControllerからViewへの更新もイベント経由

3. **責任の明確な分離**
   - View：UIの表示とユーザー入力の受け取りのみ
   - Controller：ビジネスロジック、データ管理、AxesController管理

4. **AxesControllerの管理**
   - DataController内で作成・管理
   - Viewは軸ウィジェットの設定のみ提供

5. **テスタビリティの向上**
   - イベントバスをモックすることで単体テストが容易に
   - ViewとControllerを独立してテスト可能

## 依存関係の流れ

```
MainController
    ├── DataController
    │   ├── Model (DataService)
    │   ├── AxesControllers
    │   │   ├── ImageAxesController
    │   │   ├── TraceAxesController (FluoAxes)
    │   │   └── TraceAxesController (ElecAxes)
    │   ├── ViewEventBus (View→Controller)
    │   └── ControllerEventBus (Controller→View)
    │
    └── QtDataWindow
        ├── 軸ウィジェット (PyQtGraph)
        ├── UIコントロール
        └── イベントバスへの接続
```

## 移行手順

1. バックアップの作成
2. `python migrate_to_event_driven.py`を実行
3. アプリケーションの動作確認
4. 問題があれば`.backup_[timestamp]`ファイルから復元

## 今後の拡張性

このアーキテクチャにより、以下の拡張が容易になります：
- 新しいイベントタイプの追加
- 複数のViewタイプのサポート（Web UI等）
- イベントログやデバッグ機能の追加
- リモート操作やAPI化