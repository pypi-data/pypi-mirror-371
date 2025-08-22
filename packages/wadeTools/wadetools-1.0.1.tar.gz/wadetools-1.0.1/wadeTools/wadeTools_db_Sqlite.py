import sqlite3
# commit()--事务提交
# rollback()--事务回滚
# close()--关闭一个数据库连接
# cursor()--创建一个游标


# INTEGER 整数 ， REAL 浮数 ， TEXT 字符串 ， unique 唯一

class wadeDb():
    def __init__(self,dbFilePath,tableName,typeList=({"字段名":"ID","字段类型":"TEXT unique"},{"字段名":"状态","字段类型":"TEXT"})): # dbFilePath="J:/wade.db",tableName="happy"
        self.dbFilePath = dbFilePath
        self.tableName = tableName
        self.conn = sqlite3.connect(self.dbFilePath)
        self.cursor = self.conn.cursor()
        self.typeList =typeList

    # 判断记录是否存在，返回bool
    def checkExist(self,keyName,value):
        results =self.cursor.execute(f"SELECT 1 FROM {self.tableName} WHERE {keyName} = {value} LIMIT 1")

        # print(results.fetchone())
        if results.fetchone() == None:
            return False
        else:return True

    # 创建表
    def initdb(self):
        sql = ''
        for item in self.typeList:
            # print(item)
            sql = sql + f"'{item.get('字段名')}' {item.get('字段类型')},"
        sql = sql.rstrip(',')
        # print(sql)
        create_table_sql = f'''create table IF NOT EXISTS {self.tableName}(
                            {sql}
                            )'''
        # create_table_sql = f'''create table IF NOT EXISTS {self.tableName}(
        #                             'ID' INTEGER unique,
        #                             '状态' INTEGER
        #                             )'''
        self.cursor.execute(create_table_sql)  # 执行这个语句
    # #
    def addParam(self,TableParamData:tuple):
        """新增字段，要求输入TableParamData=（列的名字，列的类型，默认值）"""
        print(TableParamData)
        try:
            self.cursor.execute(
                f"""ALTER TABLE {self.tableName} ADD COLUMN {TableParamData[0]} {TableParamData[1]} DEFAULT {
                TableParamData[2]} """)

            self.conn.commit()
        except sqlite3.OperationalError as e:
            print('数据库Exception提醒：',e)
    def getTablePrarm(self):
        # 返回该表的所有表的标题行字段内容和类型
        self.cursor.execute(f"""SELECT name, type FROM pragma_table_info('{self.tableName}')""")
        table_typeList = self.cursor.fetchall()

        table_typeList_tupe = []
        for item in table_typeList:
            table_typeList_itemJSON={}
            table_typeList_itemJSON["字段名"] = item[0]
            table_typeList_itemJSON["字段类型"] = item[1]
            table_typeList_tupe.append(table_typeList_itemJSON)
        table_typeList_tupe = tuple(table_typeList_tupe)
        # print(table_typeList_tupe)
        self.conn.commit()
        return table_typeList_tupe
    #增
    def insertdb(self,insertData:tuple):
        # 二、插入数据：执行语句即可由相同唯一列如果存在，就不会插入,
        # self.cursor.execute("insert into test (id,name,age) values (?,?,?);", [(1, 'abc', 15), (2, 'bca', 16)])
        sql1 = []
        for item in self.getTablePrarm():
            print(item)
            sql1.append(item.get('字段名'))
        sql1 = str(tuple(sql1))
        # print(sql1)
        insert_data_sql = f'''insert or ignore into {self.tableName}{sql1} values {insertData}'''
        # print(insert_data_sql)
        self.cursor.execute(insert_data_sql)
        self.conn.commit()
    # 关闭数据库
    def closedb(self,conn):
        self.conn.commit()
        self.cursor.close()

    # 查询表内所有数据
    def searchdb(self):
        '''查询所有语句，返回数据库所有内容'''
        sql = ''
        for item in self.getTablePrarm():
            # print(item)
            sql = f"'{item.get('字段名')}'," + sql
        sql = sql.rstrip(',').replace("'",'')
        search_sql = f"select {sql} from {self.tableName}"
        # print(search_sql)
        results = self.cursor.execute(search_sql)
        all_results = results.fetchall()
        # for row in all_results:
        #     print(type(row))  # type:tuple
        #     print(list(row))  # type:list
        return all_results
    # 根据表头和1种内容查询表内符合的数据,或者判断是否存在
    def searchAll_byKeyName(self,keyName,value):
        '''查询语句，返回符合条件的所有内容'''
        search_sql = f"SELECT * FROM {self.tableName} WHERE {keyName} = {value}"
        results = self.cursor.execute(search_sql)
        all_results = results.fetchall()
        # print(all_results)
        # for row in all_results:
            # print(type(row))  # type:tuple
            # print(list(row))  # type:list
        return all_results

    # 根据表头和2列内容查询表内符合的数据,或者判断是否存在
    def searchAll_byTwoKeyName(self,keyName1,value1,keyName2,value2):
        '''查询语句，返回符合条件的所有内容'''
        search_sql = f"SELECT * FROM {self.tableName} WHERE {keyName1} = {value1} and {keyName2} = {value2}"
        results = self.cursor.execute(search_sql)
        all_results = results.fetchall()
        # print(all_results)
        # for row in all_results:
            # print(type(row))  # type:tuple
            # print(list(row))  # type:list
        return all_results

        # 根据根据某个对应的值，查出想要的字段的值得里列表
    def searchNeedValue_byKeyName(self, keyName, value,needKeyName):
        """
        :param keyName: 拿来查询的字段名
        :param value:   拿来查询的索引
        :param needKeyName:   想要查询出的数据
        :return: None,Tuple
        """
        '''查询语句，返回符合条件的所有内容'''
        search_sql = f"SELECT {needKeyName} FROM {self.tableName} WHERE {keyName} = {value}"
        results = self.cursor.execute(search_sql)
        # all_results = results.fetchone()
        # print(all_results)
        # if all_results == None:
        #     return "用来查询的值不存在"
        # print(all_results)
        all_results=[]
        for row in results:
            all_results.append(row[0])
        return all_results

    #删除表内字段名符合条件的所有内容    delete(cursor,'588976817331')
    def deleteItem(self,keyName,value):
        """
        删除 符合条件的一行所有内容
        :param keyName: 指定根据哪个字段来说删除
        :param value:   字段对应的内容
        :return: None
        """
        delete_sql = f'''delete from {self.tableName} where "{str(keyName)}" = "{value}" '''
        print(delete_sql)
        self.cursor.execute(delete_sql)
        self.conn.commit()

    # 删除一整个表格    deleteTable(cursor, "happy")
    def deleteTable(self, tablename):
        check = eval(input(f"请输入四个数字8来确认删除表【{tablename}】:\n"))
        if check == 8888:
            delete_all_sql = f'drop table {self.tableName}'
            self.cursor.execute(delete_all_sql)
            self.conn.commit()
            print("数据表",tablename,"删除成功")
        else:
            print("对不起，输入有误")
    # 修改内容，只要符合的全部都会修改，只有修改唯一值，才能保证只改一行，否则所有符合条件的行都会被修改
    def updateValue(self,byKey,byKey_value,changeKey,changeKey_value):
        update_sql = f'update {self.tableName} set {changeKey}=? where {byKey}=?'
        self.cursor.execute(update_sql, (changeKey_value, byKey_value))
        self.conn.commit()
        print("修改数据成功")

    # 在表中随机取符合条件的一条
    def getOne(self,keyName,value):
        update_sql = f'SELECT *  FROM {self.tableName} WHERE {keyName} = {value} ORDER BY RANDOM() limit 1'
        results = self.cursor.execute(update_sql)
        self.conn.commit()
        result = results.fetchone()
        return result

    # 在表中随机取符合两个条件的一条
    def getOneByTwoKeys(self, keyName1, value1,keyName2,value2):
        update_sql = f'SELECT *  FROM {self.tableName} WHERE ({keyName1} = {value1}) and ({keyName2} = {value2}) ORDER BY RANDOM() limit 1'
        results = self.cursor.execute(update_sql)
        self.conn.commit()
        result = results.fetchone()
        return result
    def closeDb(self):
        self.cursor.close()
        self.conn.close()

    # 直接运行语句，返回结果中的一个
    def runSQLite(self,SQL):
        results = self.cursor.execute(SQL)
        self.conn.commit()
        result = results.fetchone()
        return result
    # 直接运行语句,返回所有结果
    def runSQLite_mode2(self,SQL):
        results = self.cursor.execute(SQL)
        self.conn.commit()
        return results
if __name__ == '__main__':
    """使用方法 创建表 新增字段  表的增删查改"""
    # 创建表，要写清楚字段格式
    from wadeTools import wadeTools_db_Sqlite

    mySql = wadeTools_db_Sqlite.wadeDb(dbFilePath="data.db", tableName='jdTable', typeList=(
        {"字段名": "字段标题1", "字段类型": "TEXT unique"},
        {"字段名": "字段标题2", "字段类型": "TEXT"},
    ))
    mySql.initdb()
    # a = mySql.getOne(keyName='字段标题2',value='22')
    a = mySql.getOneByTwoKeys(keyName1='字段标题2',value1='22',keyName2='字段标题1',value2="22")
    print(a)
    exit()

    # 新增字段，范例中创建了字段名是“姓名”，类型是TEXT，默认值是空
    mySql.addParam(TableParamData=("姓名", 'TEXT',"1"))

    # 增加一条数据 新增一条数据
    mySql.insertdb(("你好", 23, "123"))
    mySql.insertdb(("JDID2121", 23, "123"))
    mySql.insertdb(("JDID212231", 23, "123"))

    # 删除一条数据
    mySql.deleteItem(keyName="字段标题1",value="你好")

    # 删除某个数据表：
    mySql.deleteTable("jdTable")
    # 查询表内所有数据
    print(mySql.searchdb())

    # 查询 符合某个值内容的所有行
    print(mySql.searchAll_byKeyName(keyName="姓名",value="123"))

    # 查询 场景：我想要表内所有年龄18岁的人员姓名列表
    print(mySql.searchNeedValue_byKeyName(keyName="姓名",value="123",needKeyName='字段标题1'))

    # 查询某个内容是否存在,返回bool
    print(mySql.checkExist(keyName="姓名",value="123"))

    # 修改 内容，只要符合的全部都会修改，只有修改唯一值，才能保证只改一行，否则所有符合条件的行都会被修改
    mySql.updateValue(byKey="字段标题1",byKey_value="JDID2121",changeKey="字段标题2",changeKey_value="666")
