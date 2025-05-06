document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const tableBody = document.getElementById('tableBody');
    const paginationControls = document.getElementById('paginationControls');

    if (!searchInput || !tableBody || !paginationControls) return;

    const entity = searchInput.dataset.entity; // e.g. 'employees', 'barang', etc.

    let currentPage = 1;
    let typingTimer;
    const typingDelay = 300; // milliseconds

    function fetchData(search, page) {
        fetch(`/api/${entity}?search=${encodeURIComponent(search)}&page=${page}`)
            .then(response => response.json())
            .then(data => {
                updateTable(data);
                updatePagination(data.page, data.total_pages, search);
            })
            .catch(error => {
                console.error(`Error fetching ${entity}:`, error);
            });
    }

    function updateTable(data) {
        tableBody.innerHTML = '';
        let items = [];
        if (entity === 'barang') {
            items = data['barangs'] || [];
        } else if (entity === 'jenis_simpanan') {
            items = (data['jenis_simpanans'] || []).map(item => ({
                JenisId: item.JenisId,
                Keterangan: item.Keterangan,
                Operator: item.Operator
            }));
        } else if (entity === 'periode') {
            items = (data['periodes'] || []).map(item => ({
                PeriodeID: item.PeriodeID,
                Periode: item.Periode,
                Awal: item.Awal,
                Akhir: item.Akhir
            }));
        } else {
            items = data[entity] || [];
        }

        if (items.length === 0) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = tableBody.parentElement.querySelector('thead tr').children.length;
            cell.className = 'text-center py-6 text-gray-500';
            cell.textContent = `No ${entity} found.`;
            row.appendChild(cell);
            tableBody.appendChild(row);
            return;
        }
        items.forEach(item => {
            const row = document.createElement('tr');
            row.className = 'border-b border-gray-200 hover:bg-blue-100 transition duration-300';

            if (entity === 'employees') {
                row.innerHTML = `
                    <td class="py-3 px-4 whitespace-nowrap">
                        <input type="checkbox" name="selected_ids" value="${item.NIK}" class="selectItem" />
                    </td>
                    <td class="py-3 px-6 whitespace-nowrap font-medium">${item.NIK}</td>
                    <td class="py-3 px-6">${item.Nama}</td>
                    <td class="py-3 px-6">${item.Bagian}</td>
                    <td class="py-3 px-6">${item.Jabatan}</td>
                    <td class="py-3 px-6">${item.JK}</td>
                    <td class="py-3 px-6">${item.TMK}</td>
                    <td class="py-3 px-6">${item.Status ? 'Active' : 'Inactive'}</td>
                    <td class="py-3 px-6 whitespace-nowrap">
                        <a href="/employee/edit/${item.NIK}" class="text-blue-600 hover:underline mr-2">Edit</a>
                        <a href="/employee/delete/${item.NIK}" onclick="return confirm('Are you sure you want to delete this employee?');" class="text-red-600 hover:underline">Delete</a>
                    </td>
                `;
            } else if (entity === 'barang') {
                row.innerHTML = `
                    <td class="py-3 px-6 whitespace-nowrap font-medium">${item.KodeBarang}</td>
                    <td class="py-3 px-6">${item.NamaBarang}</td>
                    <td class="py-3 px-6">${item.Satuan}</td>
                    <td class="py-3 px-6">${item.Harga}</td>
                `;
            } else if (entity === 'jenis_simpanan') {
                row.innerHTML = `
                    <td class="py-3 px-6 whitespace-nowrap font-medium">${item.JenisId}</td>
                    <td class="py-3 px-6">${item.Keterangan}</td>
                    <td class="py-3 px-6">${item.Operator}</td>
                `;
            } else if (entity === 'periode') {
                row.innerHTML = `
                    <td class="py-3 px-6 whitespace-nowrap font-medium">${item.PeriodeID}</td>
                    <td class="py-3 px-6">${item.Periode}</td>
                    <td class="py-3 px-6">${item.Awal}</td>
                    <td class="py-3 px-6">${item.Akhir}</td>
                `;
            }
            tableBody.appendChild(row);
        });
        attachCheckboxListeners();
    }

    function updatePagination(page, totalPages, search) {
        paginationControls.innerHTML = '';

        function createPageLink(pageNum, text, disabled = false) {
            const link = document.createElement(disabled ? 'span' : 'a');
            link.className = disabled ? 'px-5 py-2 text-gray-400 cursor-not-allowed rounded' : 'px-5 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700 transition';
            link.textContent = text;
            if (!disabled) {
                link.href = '#';
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    currentPage = pageNum;
                    fetchData(searchInput.value, currentPage);
                });
            }
            return link;
        }

        paginationControls.appendChild(createPageLink(page - 1, '<', page <= 1));
        paginationControls.appendChild(createPageLink(page + 1, '>', page >= totalPages));
    }

    function attachCheckboxListeners() {
        const selectAll = document.getElementById('selectAll');
        const batchDeleteBtn = document.getElementById('batchDeleteBtn');
        const selectItems = document.querySelectorAll('.selectItem');

        if (selectAll) {
            selectAll.addEventListener('change', function() {
                const checked = this.checked;
                selectItems.forEach(cb => cb.checked = checked);
                if (batchDeleteBtn) batchDeleteBtn.disabled = !checked;
            });
        }

        selectItems.forEach(cb => {
            cb.addEventListener('change', function() {
                const anyChecked = Array.from(selectItems).some(cb => cb.checked);
                if (batchDeleteBtn) batchDeleteBtn.disabled = !anyChecked;
            });
        });
    }

    searchInput.addEventListener('input', function() {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => {
            currentPage = 1;
            fetchData(searchInput.value, currentPage);
        }, typingDelay);
    });

    fetchData('', 1);
});
