from django.db import models
from django.contrib import admin

# Create your models here.

# 艦船リストテーブル

class ShipList(models.Model):
	# 艦番号
	shipno       = models.IntegerField()
	# 艦名
	shipname     = models.CharField(max_length=256)

# 艦船リストテーブル管理情報

class ShipListAdmin(admin.ModelAdmin):
        list_display = ('id', 'shipno', 'shipname',)
        list_display_link = ('id', 'shipno',)
        search_fields = ['shipname']

# ワンドロテーマテーブル

class DailyThema(models.Model):
	# 日付
	date         = models.DateTimeField()
	# テーマ艦船数
	themacount   = models.IntegerField()
	# 艦船番号１
	shipno1      = models.IntegerField()
	# 艦船名１
	shipname1    = models.CharField(max_length=256)
	# 艦船番号２
	shipno2      = models.IntegerField()
	# 艦船名２
	shipname2    = models.CharField(max_length=256)
	# 艦船番号３
	shipno3      = models.IntegerField()
	# 艦船名３
	shipname3    = models.CharField(max_length=256)
	# 艦船番号４
	shipno4      = models.IntegerField()
	# 艦船名４
	shipname4    = models.CharField(max_length=256)
	# 画像収集済フラグ
	collect_flag = models.IntegerField()

# ワンドロテーマテーブル管理情報

class DailyThemaAdmin(admin.ModelAdmin): 
        list_display = ('id', 'date', 'themacount', 'shipname1', 'shipname2', 'shipname3', 'shipname4', 'collect_flag',)
        list_display_link = ('id', 'date', 'themacount', 'shipname1', 'shipname2', 'shipname3', 'shipname4', 'collect_flag',)
        search_fields = ['date']

# 管理情報登録

admin.site.register(ShipList, ShipListAdmin)
admin.site.register(DailyThema, DailyThemaAdmin)
