## はじめに
月次アップデート作業後にポリシーテンプレートも更新されるので，
新しいポリシーが現環境に影響しないかどうか確認するという作業。

新旧の差分をとって現在のポリシーと突き合わせる作業がけっこう大変だったので自動化した。
実行環境は Docker Desktop と Git が必要。

## 事前準備(初回のみ)
1. Docker Desktop と Git がない場合はインストールする
2. 任意のフォルダ内で下記を実行する
```
> git clone https://github.com/imshinjo/PolicyCompareTool.git
```
→`PolicyCompareTool`というフォルダが作成される

## 作業手順(月次)
上記の事前準備を一度終えれば，月次作業は下記の手順のみ。

1. ADからポリシーテンプレートとポリシーレポートを取得する
	- ccad02にRDPして`\\ccmaster\SYSVOL\ccmaster.kyoto-su.ac.jp\Policies\PolicyDefinitions`をクリップボード経由でローカルにコピー
	- ccad02の「PolicyReport出力」プログラムを実行して，`C:\Admin` に作成された `YYYYMMDD_PolicyReport` をローカルにコピー
    
2. 事前にアップデート済みの端末から`C:\Program Files\Microsoft OneDrive\<バージョン番号>\adm\ja\OneDrive.adml`を取得してくる

3. `PolicyDefinitions`, `YYYYMMDD_PolicyReport`, `OneDrive.adml`を，
`PolicyCompareTool`フォルダ内の`download`フォルダ下に配置する
フォルダ名，ファイル名は変更しない。（下記の通りのはず）
既存ポリシーテンプレート：`PolicyDefinitions`
既存ポリシーレポート：`YYYYMMDD_PolicyReport`
OneDriveポリシーテンプレート：`OneDrive.adml`

4. `PolicyCompareTool`フォルダで下記コマンドを実行
```
docker compose up -d standalone-chrome
docker compose run --rm docker-python
```

5. 作業フォルダに作成された output_results.txt を確認する
output_results.txt
```
 -----------------------------------------------------------
ポリシー名: Microsoft Teams を Office の新規インストール時または更新時に一緒にインストールしない | ポリシーテンプレート: office16.adml_utf-16_diff.txt | 行番号: 8087 | ポリシーレポート: /mnt/download/20250516_PolicyReport/11403_USBカメラ/Default User Policy Office&M365.html
 -----------------------------------------------------------
```
ここに出力された内容が，この自動化プログラムの最終的な出力。

onedriveの内容が変更されていた場合は
`\\ccgpmc\02_DownLoadFile\SoftWareClient系\OneDrive`
にadmデータを保存しておく。

## 出力の確認方法
この結果に出力された場合，現在OUに適用されているポリシーのタイトルが，
新旧で差分があったポリシーと合致したということなので，担当者による追加の確認が必要。

担当者は，そのポリシーが現在有効になっているのかどうか，変更内容はどういうものか，
その変更によって運用に影響するのかどうか，ということを確認する。

```
 -----------------------------------------------------------
ポリシー名: Microsoft Teams を Office の新規インストール時または更新時に一緒にインストールしない | ポリシーテンプレート: office16.adml_utf-16_diff.txt | 行番号: 8087 | ポリシーレポート: /mnt/download/20250516_PolicyReport/11403_USBカメラ/Default User Policy Office&M365.html
 -----------------------------------------------------------
```

- ポリシー名:
変更があったポリシー名を示す。

- ポリシーテンプレート:
変更の内容（新旧の差分）が書かれているファイルを示す。

- 行番号: 
上記ファイルの該当部分の行数を示す。

- ポリシーレポート:
変更があったポリシーが含まれているレポートを示す。


まとめると，担当者は下記の作業を行う。
1. プログラムを実行する
2. `output_results.txt`の内容を確認する

結果が出力されていた場合は追加で下記の作業を行う。
3. `ポリシーレポート:`のファイル内で該当の`ポリシー名:`が有効化されているか確認する
4. `ポリシーテンプレート:`のファイル内で該当の`ポリシー名:`の説明文の変更内容を確認する
5. そのポリシーの変更点が運用に影響するか評価する


## ADのポリシーテンプレートを更新する
新しいポリシーテンプレートに問題がないことを確認出来たら，ADサーバのポリシーテンプレートを更新する。
新旧ポリシーテンプレートファイルを適切に更新（上書き保存）するという作業だが，
これも手作業だといつか間違えそうなので，ツールで出力したものを使用する。

上記のツール実行手順を行うと，`PolicyCompareTool`フォルダ内の`download`フォルダ下に
`new_PolicyDefinitions`というフォルダができている。
これをローカルから`\\ccmaster\SYSVOL\ccmaster.kyoto-su.ac.jp\Policies\`にクリップボード経由でコピペする。

念のため両フォルダ内に差分がないか確認する。
```
PS \\ccmaster\SYSVOL\ccmaster.kyoto-su.ac.jp\Policies> cd .\new_PolicyDefinitions\
PS \\ccmaster\SYSVOL\ccmaster.kyoto-su.ac.jp\Policies\new_PolicyDefinitions> $targetFiles = Get-ChildItem -File -Recurse | Resolve-Path -Relative

PS \\ccmaster\SYSVOL\ccmaster.kyoto-su.ac.jp\Policies\new_PolicyDefinitions> cd ..\PolicyDefinitions\
PS \\ccmaster\SYSVOL\ccmaster.kyoto-su.ac.jp\Policies\PolicyDefinitions> $refFiles = Get-ChildItem -File -Recurse | Resolve-Path -Relative

PS \\ccmaster\SYSVOL\ccmaster.kyoto-su.ac.jp\Policies\PolicyDefinitions> Compare-Object $targetFiles $refFiles
>>
PS \\ccmaster\SYSVOL\ccmaster.kyoto-su.ac.jp\Policies\PolicyDefinitions>
```
このように出力がなければ問題ない。
足りないファイルや不要なファイルがある場合は下記のようにファイル名が表示される。
```
> Compare-Object
 $targetFiles $refFiles
>>
InputObject SideIndicator
----------- -------------
.\test.txt  =>
```

`PolicyDefinitions`と`new_PolicyDefinitions`に差分がないことを確認出来たら，フォルダを下記の通りリネームする。

1. `PolicyDefinitions`→`PolicyDefinitions_YYYYMMDD`
2. `new_PolicyDefinitions`→`PolicyDefinitions`

これで更新作業は完了となる。

ちなみに手作業で行う場合は下記を参照。
まずはフォルダ内がどのようになっているか記載する。
```
\\ccmaster\SYSVOL\ccmaster.kyoto-su.ac.jp\Policies\PolicyDefinitions
│  access16.admx
│  AccountNotifications.admx
│  ActiveXInstallService.admx
│  ...ほかにもたくさん...
└─ja-JP
        access16.adml
        AccountNotifications.adml
        ActiveXInstallService.adml
		...ほかにもたくさん...
```
このように，`PolicyDefinitions/`直下には`.admx`形式のファイルが，
`PolicyDefinitions/ja-JP/`配下には`.adml`形式のファイルがある。

`PolicyDefinitions`を複製して`PolicyDefinitions_20250520\`というように日付をつけて保存しておく
`PolicyDefinitions`と新しいポリシーテンプレートファイルで同名のファイルを見つけて上書き保存する。


## プログラムの内容
未来の自分やご担当のためにやや詳しい部分を書いておく。
これより詳細なことはコードの中に記載している。

このツールは下記の部分をプログラムで行う。
1. Webから最新のポリシーテンプレートファイルをダウンロードする
2. 既存（AD上）のポリシーテンプレートファイルとの差分を出す
3. 出てきた差分の中に，現在適用中のポリシーに関する記述がないか探す
4. 適用中のポリシーに関する変更点が見つかった場合は結果を出力する

担当者は，プログラムで収拾できないファイルを準備することと，
出てきた結果を確認して精査するだけとなる。

1.で動的サイトを扱う必要があったためseleniumを使用。
その関係でDocker環境で実行することに。
それぞれの詳細は下記の通り。

### 1.最新のポリシーテンプレートファイルを取得
これは下記の手順（ポリシーテンプレート取得先）に当たる部分で，
https://ccsql01.kyoto-su.ac.jp/knowledge/?p=18705#i-5
windows(.msi), chrome(.zip x2), edge(.zip), office(.exe) のポリシーテンプレートファイルを取得する。
それぞれ解凍や展開を行い，圧縮やアーカイブ化されていない状態にする。

### 2.新旧の差分を取得
ADからとってきたポリシーテンプレート`\\ccmaster\SYSVOL\ccmaster.kyoto-su.ac.jp\Policies\PolicyDefinitions`を複製し，
一方は 1.で取得した新しいポリシーテンプレートファイルを上書きする。

フォルダを丸ごと比較（サブフォルダ内のファイルも再帰処理）して
新旧のポリシーテンプレートファイルの差分テキストを別ファイルにまとめる。


### 3.使用中のポリシーが更新されているか確認
ADからとってきたポリシーレポートの中に書いてあるポリシー名ひとつひとつを，
出力された差分ファイルの中に含まれているポリシー名と照合する。

ポリシーレポート内のポリシー名は`gpmc_settingName=""`という属性が付与されているので，
`gpmc_settingName=""`に書かれているポリシー名で，差分ファイル内を検索する。

### 4.結果を出力する
3.の結果マッチした場合は，その内容を別のファイルに出力する。
内容は上記の「出力の確認方法」に書いてある通り。


