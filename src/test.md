



![image-20220912173000530](/home/heinz/snap/typora/72/.config/Typora/typora-user-images/image-20220912173000530.png)



nodes := {0: 'a:0', 1: 'b:0', 2: 'number', 3: 'c:0', 4: 'name:0', 5: 'string:0', 6: 'integer'}

IDs := {'number': 2, 'integer': 6, 'name:0': 4, 'c:0': 3, 'b:0': 1, 'a:0': 0, 'string:0': 5}





instantiate string



![image-20220913104252739](/home/heinz/snap/typora/72/.config/Typora/typora-user-images/image-20220913104252739.png)

duplicate b:0



original tree

![image-20220912173155313](/home/heinz/snap/typora/72/.config/Typora/typora-user-images/image-20220912173155313.png)



map_before := {0: 0, 1: 1, 2: 2, 3: 3, 5: 4, 4: 5, 6: 6}

nodes := {0: 'b', 1: 'c', 2: 'number', 3: 'name', 4: 'integer', 5: 'string'}

adding_map :=  {0: 7, 1: 8, 2: 9, 3: 10, 4: 11, 5: 12}

map_ := {0: 0, 1: 1, 7: 2, 2: 3, 3: 4, 8: 5, 9: 6, 4: 7, 5: 8, 10: 9, 11: 10, 6: 11, 12: 12}

map := {1: 0, 2: 1, 3: 2, 5: 3, 4: 4, 6: 5}

labels :=    map key, value

1 b
2 c
3 number
5 name
4 integer
6 string

![image-20220912173540286](/home/heinz/snap/typora/72/.config/Typora/typora-user-images/image-20220912173540286.png)



map_before : = {0: 7, 1: 8, 2: 9, 3: 10, 5: 12, 4: 11, 6: 6}



inv_adding_map = {7: 0, 8: 1, 9: 2, 10: 3, 11: 4, 12: 5, 0: 0, 1: 1, 2: 2, 3: 3, 4: 5, 5: 4, 6: 6}

