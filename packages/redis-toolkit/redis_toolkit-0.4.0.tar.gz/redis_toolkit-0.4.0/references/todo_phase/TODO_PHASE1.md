# Redis Toolkit 改進計畫 - Phase 1

## 📋 目標
根據架構分析報告（ARCHITECTURE_ANALYSIS_2025.md）的建議，改進 Redis Toolkit 以符合 PRINCIPLE.md 的所有核心原則。

## ✅ 高優先級工作項目（P0）

### 1. 整合 pretty-loguru（可觀察性改進）
- [x] 1.1 安裝 pretty-loguru：`pip install pretty-loguru`
- [x] 1.2 替換 redis_toolkit/core.py 中的日誌系統
  - [x] 移除現有的 logging import
  - [x] 改用 `from pretty_loguru import create_logger`
  - [x] 更新所有 logger.info/debug/error 呼叫
- [x] 1.3 更新 redis_toolkit/pool_manager.py 的日誌系統
- [x] 1.4 更新 redis_toolkit/utils/retry.py 的日誌系統
- [x] 1.5 在 pyproject.toml 和 requirements.txt 加入 pretty-loguru 依賴
- [x] 1.6 測試日誌輸出格式是否符合預期

### 2. 完善配置管理系統
- [x] 2.1 評估是否需要支援配置檔案（JSON/YAML）- 決定：作為函式庫不應依賴配置檔案
- [x] 2.2 在 RedisOptions 中加入配置驗證方法
  ```python
  def validate(self) -> None:
      """驗證配置的有效性"""
      if self.max_connections and self.max_connections < 1:
          raise ValueError("max_connections 必須大於 0")
      # 其他驗證規則
  ```
- [x] 2.3 為 RedisConnectionConfig 加入更多配置選項
  - [x] connection_timeout
  - [x] socket_timeout
  - [x] retry_on_timeout
  - [x] health_check_interval
  - [x] SSL/TLS 支援
- [x] 2.4 更新文檔說明新的配置選項

### 3. 補充核心文檔
- [x] 3.1 創建 docs/ 目錄
- [x] 3.2 編寫 docs/API.md
  - [x] 列出所有公開方法的詳細說明
  - [x] 包含參數、返回值、異常說明
  - [x] 提供使用範例
- [x] 3.3 編寫 docs/QUICKSTART.md
  - [x] 安裝說明
  - [x] 基本使用範例
  - [x] 常見使用場景
- [x] 3.4 創建 docs/CHANGELOG.md
  - [x] 記錄版本更新歷史
  - [x] 從 0.3.0 版本開始記錄

## ✅ 中優先級工作項目（P1）

### 4. 完善範例程式
- [x] 4.1 創建 examples/basic_usage.py
  - [x] 展示基本的 set/get 操作
  - [x] 展示兩種初始化方式
- [x] 4.2 創建 examples/batch_operations.py
  - [x] 批次設定和取得範例
  - [x] 性能比較展示
- [x] 4.3 創建 examples/pubsub_example.py
  - [x] 發布者和訂閱者範例
  - [x] 多頻道訂閱展示
- [x] 4.4 創建 examples/image_transfer.py
  - [x] 圖片編碼和解碼範例
  - [x] 透過 Redis 傳輸圖片
- [x] 4.5 創建 examples/audio_streaming.py
  - [x] 音頻數據處理範例
- [x] 4.6 創建 examples/video_caching.py
  - [x] 視頻緩存範例

### 5. 實現 @with_retry 裝飾器
- [x] 5.1 在 redis_toolkit/utils/retry.py 中實現 @with_retry
  ```python
  def with_retry(max_attempts=3, delay=0.1, backoff=2.0):
      """重試裝飾器，支援指數退避"""
      def decorator(func):
          @functools.wraps(func)
          def wrapper(*args, **kwargs):
              return simple_retry(func, max_attempts, delay, backoff, *args, **kwargs)
          return wrapper
      return decorator
  ```
- [x] 5.2 在 RedisToolkit 的關鍵方法上應用 @with_retry
- [x] 5.3 更新測試以驗證裝飾器功能

### 6. 測試覆蓋率提升
- [x] 6.1 安裝 coverage 工具：`pip install coverage`
- [x] 6.2 測量當前覆蓋率：`pytest --cov=redis_toolkit --cov-report=html`
- [x] 6.3 識別未覆蓋的代碼區域
- [x] 6.4 補充單元測試，目標達到 65% 覆蓋率（實際達到 69%）
- [ ] 6.5 在 CI/CD 中加入覆蓋率檢查

## ✅ 低優先級工作項目（P2）

### 7. 重構長函數
- [x] 7.1 分析 _subscriber_loop 函數（約60行）
- [x] 7.2 將 _subscriber_loop 拆分為更小的函數
  - [x] _initialize_pubsub
  - [x] _read_and_process_message
  - [x] _handle_connection_error
  - [x] _handle_unexpected_error
  - [x] _cleanup_pubsub
- [x] 7.3 簡化 _format_log 函數（拆分為多個輔助函數）
- [x] 7.4 確保重構後所有測試通過

### 8. 性能基準測試
- [x] 8.1 創建 benchmarks/ 目錄
- [x] 8.2 編寫批次操作性能測試
- [x] 8.3 編寫序列化性能測試
- [x] 8.4 編寫連接池效率測試
- [x] 8.5 生成性能報告並記錄基準值

## 🔍 驗收標準

### Phase 1 完成標準：
1. ✅ pretty-loguru 已整合，所有日誌使用新格式
2. ✅ 配置管理系統支援驗證功能
3. ✅ 核心文檔（API.md、QUICKSTART.md）已完成

### Phase 2 完成標準：
1. ✅ 所有 6 個範例程式可正常運行
2. ✅ @with_retry 裝飾器已實現並應用
3. ✅ 測試覆蓋率達到 65% 以上

### Phase 3 完成標準：
1. ✅ 長函數已重構，每個函數不超過 30 行
2. ✅ 性能基準測試套件完整
3. ✅ 所有改進項目都有對應的測試

## 📝 注意事項

1. 每完成一個工作項目都要運行測試確保沒有破壞現有功能
2. 遵循 PRINCIPLE.md 中的所有開發原則
3. 使用 pretty-loguru 時要保持日誌格式的一致性
4. 文檔要包含充分的範例代碼
5. 優先完成 P0 項目，它們對專案合規性影響最大

---
建立時間：2025-07-28
最後更新：2025-07-28
狀態：Phase 1 所有任務已完成（除了 6.5 CI/CD 覆蓋率檢查，根據用戶要求跳過）
負責人：Redis Toolkit Team