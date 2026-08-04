async function exportarPDF() {
  document.body.classList.add('exportando-pdf');
  const { jsPDF } = window.jspdf;
  const pdf = new jsPDF({ orientation: 'landscape', unit: 'px', format: [1280, 720] });

  const slides = document.querySelectorAll('.slide');
  for (let i = 0; i < slides.length; i++) {
    const canvas = await html2canvas(slides[i], { scale: 2 });
    const img = canvas.toDataURL('image/jpeg', 0.92);
    if (i > 0) pdf.addPage([1280, 720], 'landscape');
    pdf.addImage(img, 'JPEG', 0, 0, 1280, 720);
  }

  pdf.save(`informe-${STORE.periodo.anio}-${String(STORE.periodo.mes + 1).padStart(2, '0')}.pdf`);
  document.body.classList.remove('exportando-pdf');
}
