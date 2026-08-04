function leerArchivo(file) {
  return new Promise((resolve, reject) => {
    const lector = new FileReader();
    lector.onload = e => {
      try {
        resolve(XLSX.read(e.target.result, { type: 'binary' }));
      } catch (err) {
        reject(err);
      }
    };
    lector.onerror = reject;
    lector.readAsBinaryString(file);
  });
}

function filasDeHoja(wb, nombreHoja) {
  if (!wb.SheetNames.includes(nombreHoja)) return null;
  return XLSX.utils.sheet_to_json(wb.Sheets[nombreHoja], { defval: '' });
}

// Las hojas del consolidado real traen, además de los tickets, una tabla
// dinámica y/o una celda de referencia de gráfico en las MISMAS filas de la
// hoja (a la derecha o debajo de los datos). XLSX.js las lee igual que
// cualquier otra fila, con los encabezados de la fila 1 — así que sin
// filtrar, el conteo queda inflado con "filas" que en realidad son la
// tabla dinámica. Un ticket real siempre tiene "Fecha de apertura"; la
// tabla dinámica y la celda de referencia del gráfico, verificado contra
// Dta junio.xlsx, nunca caen en esa columna. Ese es el filtro.
function filasValidas(filas) {
  return filas.filter(f => String(f['Fecha de apertura'] || '').trim() !== '');
}

function validarColumnas(wb) {
  const avisos = [];
  Object.entries(CONFIG.hojasRequeridas).forEach(([hoja, columnasEsperadas]) => {
    const filas = filasDeHoja(wb, hoja);
    if (filas === null) {
      avisos.push(`Falta la hoja "${hoja}" en el archivo.`);
      return;
    }
    if (!filas.length) return; // hoja presente pero vacía: válido, sin casos ese mes
    const columnas = Object.keys(filas[0]);
    const faltantes = columnasEsperadas.filter(c => !columnas.includes(c));
    if (faltantes.length) {
      avisos.push(`Hoja "${hoja}": faltan columnas ${faltantes.join(', ')}.`);
    }
  });
  return avisos;
}

function cargarConsolidado(wb) {
  const contar = hoja => {
    const filas = filasDeHoja(wb, hoja);
    return filas ? filasValidas(filas).length : 0;
  };

  STORE.indicadores.casos = {
    requerimientos: contar('Reque_SO'),
    alertas: contar('Alerta_SO'),
    casos_bd: contar('Requerimientos BD'),
    historico: [],
  };
}
