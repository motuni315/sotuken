
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        const csrftoken = getCookie('csrftoken');

        window.onload = function() {
        if (navigator.userAgent.match(/iPhone|Android/i)) {
        }
            // カメラを起動させるinput
            document.getElementById('image').setAttribute('capture', 'camera');
            document.getElementById('image').setAttribute('accept', 'image/*');
        }


        function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                console.log("Position successfully obtained:", position);
                showPosition(position);
            },
            (error) => {
                console.log("Error obtaining position:", error);
                showError(error);
            });
    } else {
        alert("このブラウザでは位置情報がサポートされていません。");
    }
}

        function showPosition(position) {
            document.getElementById('lost_location').value = position.coords.latitude + ", " + position.coords.longitude;
        }

        function showError(error) {
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    alert("位置情報の取得が拒否されました。");
                    break;
                case error.POSITION_UNAVAILABLE:
                    alert("位置情報が利用できません。");
                    break;
                case error.TIMEOUT:
                    alert("位置情報の取得がタイムアウトしました。");
                    break;
                case error.UNKNOWN_ERROR:
                    alert("不明なエラーが発生しました。");
                    break;
            }
        }

        // 現在の日時を取得して拾った時間欄に自動入力
        function getCurrentDateTime() {
            const now = new Date();
            const year = now.getFullYear();
            const month = ('0' + (now.getMonth() + 1)).slice(-2);
            const day = ('0' + now.getDate()).slice(-2);
            const hours = ('0' + now.getHours()).slice(-2);
            const minutes = ('0' + now.getMinutes()).slice(-2);
            const seconds = ('0' + now.getSeconds()).slice(-2);
            return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
        }

        // ラベルマッピング辞書
        const labelMapping = {
            'Credit Card': 'クレジットカード',
            'ID Card': '証明書',
            'Electronics': '電子機器',
            'Phone': '携帯電話'
            // 必要に応じて他のラベルを追加
        };

        // 画像が選択されたときにラベル検出を行う
        function detectLabels() {
            const formData = new FormData();
            const imageFile = document.getElementById('image').files[0];
            if (!imageFile) return;

            formData.append('image', imageFile);

            // 非同期でラベル検出APIにリクエスト
            fetch('/detect_labels_api/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrftoken  // CSRFトークンを追加
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // 検出結果のラベルをフォームに反映
                    const detectedLabels = data.labels;
                    let itemName = '不明';
                    let genre = '不明';
                    let color = '不明';

                    detectedLabels.forEach(label => {
                        if (labelMapping[label]) {
                            if (label === 'Credit Card' || label === 'ID Card') {
                                itemName = labelMapping[label];
                            } else if (label === 'Electronics' || label === 'Phone') {
                                genre = labelMapping[label];
                            }
                        }
                    });

                    document.getElementById('item_name').value = itemName;
                    document.getElementById('genre').value = genre;
                    document.getElementById('color').value = color;

                    // 検出結果を表示エリアに表示
                    document.getElementById('detected_labels').innerHTML =
                        `<p>検出されたラベル:</p>
                            <ul>
                                ${detectedLabels.map(label => `<li>${label}</li>`).join('')}
                            </ul>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("ラベル検出に失敗しました。");
            });
        }

        window.onload = function() {
            getLocation();  // ページがロードされたときに位置情報を取得
            document.getElementById('found_time').value = getCurrentDateTime();  // 現在時刻を拾った時間に自動入力
            document.getElementById('image').onchange = detectLabels;  // 画像が選択されたらラベル検出
        }
