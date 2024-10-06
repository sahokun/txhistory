"----------------------------------------
" 基本設定
"----------------------------------------
set encoding=utf-8                 " バッファの文字コードをUTF-8に設定
set fileencodings=iso-2022-jp,euc-jp,sjis,utf-8  " ファイルの文字コードの自動判別
set fileformats=unix,dos,mac      " 改行コードの自動判別

" バックアップとスワップファイル関連 (必要に応じてコメントアウト解除)
" set nowritebackup                " 上書き保存時にバックアップを作成しない
" set nobackup                    " バックアップファイルを作成しない
" set noswapfile                  " スワップファイルを作成しない

set virtualedit=block              " 矩形選択で文字がなくても右へ移動可能
set backspace=indent,eol,start    " バックスペースキーの動作を拡張
set ambiwidth=double              " 全角文字を2文字幅で表示
set wildmenu                      " コマンドライン補完でワイルドカードを使用可能

"----------------------------------------
" 検索設定
"----------------------------------------
set ignorecase                    " 検索時に大文字小文字を区別しない
set smartcase                     " 小文字で検索開始時は大文字小文字を区別しない
set wrapscan                      " 検索がファイル末尾に達したら先頭に戻る
set incsearch                     " インクリメンタルサーチ
set hlsearch                      " 検索結果をハイライト表示

"----------------------------------------
" 表示設定
"----------------------------------------
set nofoldenable                  " 検索行以外を折りたたむ(フォールドする)機能を無効化
set noerrorbells                  " エラー時にビープ音を鳴らさない
set shellslash                    " パスの区切り文字をスラッシュにする
set showmatch matchtime=1         " 対応する括弧を強調表示
set cinoptions+=:0                " インデント設定 (C言語など)
set cmdheight=2                   " コマンドラインの高さを2行にする
set laststatus=2                  " ステータスラインを常に表示
set showcmd                       " コマンドラインに入力中のコマンドを表示
set display=lastline              " 最後の行が途中で途切れないように表示
set list                          " 不可視文字を表示 (タブは ^I、行末は $)
set listchars=tab:^\ ,trail:~     " タブと行末の空白を表示
set history=10000                 " コマンドラインの履歴を10000件保存
hi Comment ctermfg=3              " コメントを水色で表示 (ターミナル)

"----------------------------------------
" インデント設定
"----------------------------------------
set expandtab                     " タブをスペースに展開
set shiftwidth=2                  " インデント幅 (スペース2つ)
set softtabstop=2                 " タブキーで挿入されるスペースの数
set tabstop=2                     " 表示上のタブ幅

"----------------------------------------
" GUI 設定 (GVim の場合)
"----------------------------------------
set guioptions-=T                 " ツールバーを非表示
set guioptions+=a                 " ヤンクでクリップボードにコピー
set guioptions-=m                 " メニューバーを非表示
set guioptions+=R                 " 右スクロールバーを非表示

"----------------------------------------
" その他設定
"----------------------------------------
set showmatch                     " 対応する括弧を強調表示
set smartindent                   " スマートインデント
set title                         " ウィンドウタイトルにファイル名を表示
set number                        " 行番号を表示
set clipboard=unnamed,autoselect  " ヤンクでクリップボードにコピー

nnoremap <Esc><Esc> :nohlsearch<CR><ESC> " Esc 2回で検索ハイライトを解除
syntax on                         " シンタックスハイライトを有効にする
set nrformats=                    " 行番号を10進数で表示
set whichwrap=b,s,h,l,<,>,[,],~   " 行末でのカーソル移動をスムーズにする
" set mouse=a                     " マウス操作を有効にする
set mouse=n                       " マウス操作をノーマル時のみ (ビジュアルでコピー可)

"----------------------------------------
" 自動コマンド
"----------------------------------------
augroup source-vimrc               " .vimrc ファイルを自動で再読み込み
  autocmd!
  autocmd BufWritePost *vimrc source $MYVIMRC | set foldmethod=marker
  autocmd BufWritePost *gvimrc if has('gui_running') source $MYGVIMRC
augroup END

augroup auto_comment_off           " コメントの自動挿入を無効にする
  autocmd!
  autocmd BufEnter * setlocal formatoptions-=r
  autocmd BufEnter * setlocal formatoptions-=o
augroup END

augroup remember_cursor_position   " カーソル位置の記憶
  autocmd!
  autocmd BufReadPost *
    \ if line("'\"") > 0 && line ("'\"") <= line("$") |
    \   exe "normal! g'\"" |
    \ endif
augroup END

augroup set_textwidth_for_txt      " テキストファイルの幅の設定
  autocmd!
  autocmd BufRead *.txt set tw=78
augroup END
