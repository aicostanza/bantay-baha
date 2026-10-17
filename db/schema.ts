import {sqliteTable,integer,real,text} from 'drizzle-orm/sqlite-core';
export const readings=sqliteTable('readings',{id:integer('id').primaryKey({autoIncrement:true}),sensorId:text('sensor_id').notNull(),waterLevelCm:real('water_level_cm').notNull(),timestamp:text('timestamp').notNull()});
