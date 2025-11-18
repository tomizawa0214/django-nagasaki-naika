module.exports = {
  "extends": [
    // 順番に注意
    "stylelint-config-standard-scss",
    "stylelint-config-recess-order",
    "stylelint-config-prettier-scss"
  ],
  ignoreFiles: [
    // 除外するファイルを指定
    '**/node_modules/**',
  ],
  rules: {
    // ベンダープレフィックスの統一化を無効化
    "property-no-vendor-prefix": null,
    // コメントの整形を無効化
    "comment-empty-line-before": null,
    // クラス名の命名規則チェックを無効化
    "selector-class-pattern": null,
    // メディアクエリの演算子
    "media-feature-range-notation": "prefix",
  }
};