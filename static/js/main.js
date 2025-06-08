// يمكن إضافة أي وظائف جافاسكريبت عامة هنا
document.addEventListener('DOMContentLoaded', function() {
    // تفعيل عناصر التلميح (tooltips)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // إخفاء رسائل التنبيه بعد 5 ثواني
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            bootstrap.Alert.getOrCreateInstance(alert).close();
        });
    }, 5000);
});