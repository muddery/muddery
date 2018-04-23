
$(function(){
    var table_name = getQueryString("table");
    var url = window.location.protocol + "//" + window.location.host + "/worlddata/editor/api/table";
    
    $("#table").bootstrapTable({ // 对应table标签的id
        url: url,
        method: 'post',
        cache: false,
        striped: true,
        pagination: true,
        pageList: [20, 50, 100],
        pageSize: 20,
        sidePagination: 'client',
        queryParams: function (params) {
          return {
              table: table_name,
              pageSize: params.limit,
              offset: params.offset,
              sort: params.sort,
              sortOrder: params.order,
          }
        },
        sortName: 'id',
        sortOrder: 'desc',
        search: true,
        clickToSelect: true,
        singleSelect: true,
        onLoadSuccess: function(){  //加载成功时执行
            console.info("加载成功");
        },
        onLoadError: function(){  //加载失败时执行
            console.info("加载数据失败");
        }
    });
});
