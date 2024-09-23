# AIWolfNLPHumanAgent

> [!CAUTION]
> 現在のバージョンはデモ用であり、動作を保証するものではありません。
> 現在はSSH接続のみなど、対応できていないものが多くあります。
> また、以下の手順でもできなくなっている可能性もあります。
> 正式リリースまで今しばらくお待ちください。

## 手順

1. 自身の仮想環境などを用意してください。
1. このリポジトリをクローン後、以下のコマンドを実行してください。
    ```sh
    $ pip install -r requirement.txt
    ```
1. その後、以下のコマンドを実行してください。
    ```
    # pip install -i https://test.pypi.org/simple/ aiwolf-nlp-common==0.0.18
    ```

## 実行方法
基本的に [AIWolfNLAgentPython](https://github.com/aiwolfdial/AIWolfNLAgentPython)と同じです。

1. `res/`以下に`config.ini`,`ssh-config`を作成する
1. 作成したファイルを自身の設定に合うように修正する
1. 以下のコマンドを実行する
    ```
    $ python3 main.py
    ```