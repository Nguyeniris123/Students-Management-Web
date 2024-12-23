function addScore(studentId, scoreType) {
    const scoreValue = prompt("Nhập điểm cần thêm:");
    if (!scoreValue) {
        alert("Bạn chưa nhập điểm.");
        return;
    }

    fetch('/admin/scoreview/add_score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            student_id: studentId,
            subject_id: document.getElementById("subject").value,
            score_type: scoreType,
            score_value: parseFloat(scoreValue)
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        if (data.success) {
            location.reload();
        }
    })
    .catch(error => {
        console.error('Lỗi:', error);
        alert('Không thể thêm điểm. Vui lòng thử lại.');
    });
}


function editScore(scoreId, currentValue) {
    const newScore = prompt('Nhập điểm mới:', currentValue);

    if (newScore !== null) {
        fetch('/admin/scoreview/edit_score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ score_id: scoreId, new_value: parseFloat(newScore) }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Sửa điểm thành công!');
                location.reload(); // Tải lại trang
            } else {
                alert(`Lỗi: ${data.message}`);
            }
        })
        .catch(error => {
            alert(`Lỗi: ${error.message}`);
        });
    }
}


function deleteScore(scoreId) {
    if (confirm("Bạn có chắc chắn muốn xóa điểm này không?")) {
        fetch('/admin/scoreview/delete_score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ score_id: scoreId }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                location.reload(); // Tải lại trang để cập nhật danh sách điểm
            } else {
                alert("Lỗi: " + data.message);
            }
        })
        .catch(error => {
            console.error("Lỗi khi xóa điểm:", error);
            alert("Đã xảy ra lỗi khi xóa điểm.");
        });
    }
}

